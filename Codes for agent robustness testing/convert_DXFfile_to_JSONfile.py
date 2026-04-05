import json
import ezdxf
import os


def convert_DXFfile_to_JSONfile(json_input_path: str) -> str:
    # 1. 清理路径
    json_input_path = json_input_path.strip().replace('"', '')

    # 2. 读取 Global_Data.json
    with open(json_input_path, 'r') as file:
        global_config = json.load(file)

    # 3. 读取次级基础设施信息 JSON
    infra_info_path = global_config['infrastructure_information']
    with open(infra_info_path, 'r') as file:
        infra_data = json.load(file)

    # 获取 DXF 文件列表 (假设键名为 'network_dxf_files')
    network_files = infra_data.get('network_dxf_files', [])

    all_network_data = {'nodes': [], 'edges': []}

    for dxf_path in network_files:
        if not os.path.exists(dxf_path):
            continue

        # 4. 加载 DXF 文件
        try:
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
        except Exception as e:
            print(f"无法读取文件 {dxf_path}: {e}")
            continue

        # 5. 提取节点 (POINT 实体)
        # 注意：DXF 点实体通常不带复杂属性，我们使用其图层名作为类型，坐标作为核心信息
        for point in msp.query('POINT'):
            coords = point.dxf.location
            all_network_data['nodes'].append({
                'Code': str(point.dxf.handle),  # 使用 DXF 句柄作为唯一代码
                'Facility': "Infrastructure Node",
                'Service Area': "Unknown",
                'Location': "Unknown",
                'Demands': "None",
                'Coordinates': [coords.x, coords.y],
                'Infrastructure Type': point.dxf.layer  # 图层名通常代表设施类型
            })

        # 6. 提取边 (LINE 和 LWPOLYLINE 实体)
        # 处理直线 (LINE)
        for line in msp.query('LINE'):
            start = line.dxf.start
            end = line.dxf.end
            all_network_data['edges'].append({
                'Code': str(line.dxf.handle),
                'Start': [start.x, start.y],
                'End': [end.x, end.y],
                'Infrastructure Type': line.dxf.layer
            })

        # 处理多段线 (LWPOLYLINE)
        for pline in msp.query('LWPOLYLINE'):
            points = list(pline.get_points())
            # 将多段线拆分为一系列的两点连线（边）
            if len(points) >= 2:
                for i in range(len(points) - 1):
                    all_network_data['edges'].append({
                        'Code': f"{pline.dxf.handle}_{i}",
                        'Start': [points[i][0], points[i][1]],
                        'End': [points[i + 1][0], points[i + 1][1]],
                        'Infrastructure Type': pline.dxf.layer
                    })

    # 7. 保存生成的 JSON 文件
    output_json_path = 'infrastructure_networks.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(all_network_data, outfile, indent=4)

    # 8. 更新 Global_Data.json
    global_config['infrastructure_networks'] = output_json_path
    with open(json_input_path, 'w') as file:
        json.dump(global_config, file, indent=4)

    return "The path to infrastructure_networks has been saved in Global_data.json"