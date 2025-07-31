import json
import random
import shapely.geometry as geom
import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
import networkx as nx
import uuid
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import matplotlib.lines as mlines

# 配置
NUM_AREAS = 35
INFRA_TYPES = {
    "gas": ["Intersection node", "Gate Station", "Regulator Station"],
    "water": ["Elevated Tank", "Intersection node", "Pumping Station"],
    "power": ["12kv Substation", "23kv Substation", "Intersection node", "Gate Station"]
}
FACILITY_MARKERS = {
    "Intersection node": "o",
    "Gate Station": "s",
    "Regulator Station": "^",
    "Elevated Tank": "D",
    "Pumping Station": "P",
    "12kv Substation": "v",
    "23kv Substation": "<"
}
INFRA_COLORS = {
    "gas": (255/255, 215/255, 87/255),      # 黄色系
    "water": (0/255, 0/255, 255/255),       # 蓝色
    "power": (0/255, 128/255, 0/255)        # 绿色
}

# 生成不规则多边形区域
def generate_irregular_polygon(center=(0, 0), radius=1.0, num_vertices=30):
    points = []
    for i in range(num_vertices):
        angle = 2 * np.pi * i / num_vertices
        r = radius * (0.8 + 0.4 * random.random())
        x = center[0] + r * np.cos(angle)
        y = center[1] + r * np.sin(angle)
        points.append((x, y))
    return Polygon(points).buffer(0)

# 用Voronoi生成区域
def generate_curved_areas(region, num_areas):
    minx, miny, maxx, maxy = region.bounds
    points = np.random.rand(num_areas, 2)
    points[:, 0] = minx + points[:, 0] * (maxx - minx)
    points[:, 1] = miny + points[:, 1] * (maxy - miny)
    vor = Voronoi(points)
    areas = []
    for region_index in vor.point_region:
        region_pts = vor.regions[region_index]
        if not region_pts or -1 in region_pts:
            continue
        poly = Polygon([vor.vertices[i] for i in region_pts])
        clipped = poly.intersection(region)
        if clipped.is_empty or not clipped.is_valid:
            continue
        areas.append(clipped.buffer(0))
    return areas[:num_areas]

# 计算连接概率，距离越近概率越大
def edge_connection_probability(distance, decay_rate=5):
    return np.exp(-decay_rate * distance)

# 生成折线边，两段线，中间点带扰动，确保在区域内
def generate_polyline_edge(x0, y0, x1, y1, region, max_attempts=30):
    for _ in range(max_attempts):
        mid_x = (x0 + x1) / 2 + np.random.uniform(-0.02, 0.02)
        mid_y = (y0 + y1) / 2 + np.random.uniform(-0.02, 0.02)
        coords = [(x0, y0), (mid_x, mid_y), (x1, y1)]
        line = LineString(coords)
        if region.contains(line):
            return coords
    # 无法找到满足的折线则退回直线
    return [(x0, y0), (x1, y1)]

# 生成基础设施节点
nodes = []
region = generate_irregular_polygon(center=(40, 80), radius=1.0)
areas = generate_curved_areas(region, NUM_AREAS)


for i, area in enumerate(areas):
    area_code = f"A{i+1}"
    num_nodes = random.randint(2, 5)
    for _ in range(num_nodes):
        infra_type = random.choice(list(INFRA_TYPES.keys()))
        facility = random.choice(INFRA_TYPES[infra_type])
        # 确保点在区域内
        while True:
            x = random.uniform(area.bounds[0], area.bounds[2])
            y = random.uniform(area.bounds[1], area.bounds[3])
            p = Point(x, y)
            if area.contains(p):
                break
        node = {
            "Code": str(uuid.uuid4())[:6],
            "Facility": facility,
            "Service Area": None,
            "Location": area_code,
            "Demands": random.choice(["power", "water", "gas"]),
            "Coordinates": [x, y],
            "Infrastructure Type": infra_type
        }
        nodes.append(node)

# ...（其余代码保持不变）

# 在生成节点之后，添加 Service Area 自动分配逻辑
# 定义供给类设施
supply_facilities = {"Pumping Station", "12kv Substation", "23kv Substation", "Elevated Tank", "Gate Station"}
area_codes = [f"A{i+1}" for i in range(len(areas))]

for node in nodes:
    if node["Facility"] in supply_facilities:
        num_service_areas = random.randint(1, 3)
        node["Service Area"] = random.sample(area_codes, num_service_areas)
    else:
        node["Service Area"] = None


# 根据距离生成边，并确保每个基础设施图连通
edges = {"gas": [], "water": [], "power": []}
for infra_type in ["gas", "water", "power"]:
    relevant_nodes = [n for n in nodes if n["Infrastructure Type"] == infra_type]
    node_dict = {n["Code"]: n for n in relevant_nodes}
    coords = np.array([n["Coordinates"] for n in relevant_nodes])
    codes = [n["Code"] for n in relevant_nodes]

    dist_matrix = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=2)
    G = nx.Graph()
    for code in codes:
        G.add_node(code)

    # 添加概率边
    for i in range(len(codes)):
        for j in range(i+1, len(codes)):
            p = edge_connection_probability(dist_matrix[i, j])
            if np.random.rand() < p:
                G.add_edge(codes[i], codes[j])

    # 确保每个节点至少有一条边（孤立点连接最近邻）
    for i, code in enumerate(codes):
        if G.degree[code] == 0:
            dists = dist_matrix[i]
            idx = np.argsort(dists)
            for candidate_idx in idx[1:]:
                if codes[candidate_idx] != code:
                    G.add_edge(code, codes[candidate_idx])
                    break

    # 保证图连通
    components = list(nx.connected_components(G))
    if len(components) > 1:
        main_comp = max(components, key=len)
        main_nodes = set(main_comp)
        for comp in components:
            if comp == main_comp:
                continue
            comp_nodes = set(comp)
            min_dist = np.inf
            edge_to_add = None
            for n1 in comp_nodes:
                idx1 = codes.index(n1)
                for n2 in main_nodes:
                    idx2 = codes.index(n2)
                    d = dist_matrix[idx1, idx2]
                    if d < min_dist:
                        min_dist = d
                        edge_to_add = (n1, n2)
            if edge_to_add:
                G.add_edge(*edge_to_add)

    # 生成折线边坐标存储
    edges[infra_type] = []  # 清空旧边
    for u, v in G.edges():
        x0, y0 = node_dict[u]["Coordinates"]
        x1, y1 = node_dict[v]["Coordinates"]
        polyline_coords = generate_polyline_edge(x0, y0, x1, y1, region)
        edges[infra_type].append({"from": u, "to": v, "coords": polyline_coords})

# 保存网络json文件
# 保存网络json文件
infrastructure_data = {"nodes": nodes, "edges": edges}
with open("infrastructure_networks_S4.json", "w") as f:
    json.dump(infrastructure_data, f, indent=2)

# 保存区域shp文件
gdf = gpd.GeoDataFrame({"Area": [f"A{i+1}" for i in range(len(areas))]}, geometry=areas)
gdf.set_crs(epsg=4326).to_file("region_areas_S4.shp")

# 自定义绘制带边框的高辨识度标记函数
def draw_custom_marker(ax, x, y, shape, color, size=0.03, edge_color='black', linewidth=1.5):
    """在ax上绘制带边框自定义形状标记"""
    if shape == "circle":
        patch = patches.Circle((x, y), size, facecolor=color, edgecolor=edge_color, lw=linewidth)
    elif shape == "square":
        patch = patches.RegularPolygon((x, y), numVertices=4, radius=size, orientation=np.pi/4,
                                      facecolor=color, edgecolor=edge_color, lw=linewidth)
    elif shape == "triangle_up":
        patch = patches.RegularPolygon((x, y), numVertices=3, radius=size, orientation=0,
                                      facecolor=color, edgecolor=edge_color, lw=linewidth)
    elif shape == "triangle_down":
        patch = patches.RegularPolygon((x, y), numVertices=3, radius=size, orientation=np.pi,
                                      facecolor=color, edgecolor=edge_color, lw=linewidth)
    elif shape == "diamond":
        patch = patches.RegularPolygon((x, y), numVertices=4, radius=size, orientation=0,
                                      facecolor=color, edgecolor=edge_color, lw=linewidth)
    elif shape == "star":
        # 五角星暂用大圆代替，可自行扩展更复杂Path绘制
        patch = patches.Circle((x, y), size, facecolor=color, edgecolor=edge_color, lw=linewidth)
    elif shape == "half_circle":
        # 半圆拼色：左半实色，右半白色
        wedge1 = patches.Wedge((x, y), size, 90, 270, facecolor=color, edgecolor=edge_color, lw=linewidth)
        wedge2 = patches.Wedge((x, y), size, 270, 90, facecolor='white', edgecolor=edge_color, lw=linewidth)
        ax.add_patch(wedge1)
        ax.add_patch(wedge2)
        return
    else:
        patch = patches.Circle((x, y), size, facecolor=color, edgecolor=edge_color, lw=linewidth)

    ax.add_patch(patch)

def create_legend_patch(shape, color, label):
    """
    创建适用于图例的简化图形符号，使用 Line2D 模拟各种形状。
    RegularPolygon 不能被 legend 正确渲染，我们使用 Line2D 替代。
    """
    marker_dict = {
        "circle": "o",
        "square": "s",
        "triangle_up": "^",
        "triangle_down": "v",
        "diamond": "D",
        "star": "*",
        "half_circle": "o"  # 仍然用圆代替，图例中无法显示拼色
    }
    marker = marker_dict.get(shape, "o")
    return mlines.Line2D([], [], color=color, marker=marker, linestyle='None',
                         markeredgecolor='black', markersize=10, label=label)

# 绘图函数，使用自定义标记，去除图例和网格
def plot_network_by_type(infra_type, nodes, edges, areas, region, point_size=60, line_width=1):
    fig, ax = plt.subplots(figsize=(8,8))
    ax.set_facecolor("white")

    # 大区域统一深灰色填充
    fill_color = (252/255, 234/255, 234/255)
    x, y = region.exterior.xy
    ax.fill(x, y, color=fill_color, alpha=1)

    # 小区域仅绘制边界
    for poly in areas:
        x, y = poly.exterior.xy
        ax.plot(x, y, color=(237/255, 132/255, 73/255), linewidth=2)
        for interior in poly.interiors:
            xh, yh = zip(*interior.coords)
            ax.fill(xh, yh, color='white', alpha=1)

    node_dict = {n["Code"]: n for n in nodes if n["Infrastructure Type"] == infra_type}
    color = INFRA_COLORS[infra_type]

    # 绘制边
    for edge in edges[infra_type]:
        xs, ys = zip(*edge["coords"])
        ax.plot(xs, ys, color=color, linewidth=line_width)

    # 节点形状映射
    shape_map = {
        "Intersection node": "circle",
        "Gate Station": "square",
        "Regulator Station": "triangle_up",
        "Elevated Tank": "triangle_down",
        "Pumping Station": "diamond",
        "12kv Substation": "half_circle",
        "23kv Substation": "star"
    }
    size = 0.05

    # 绘制节点
    for node in node_dict.values():
        x, y = node["Coordinates"]
        fac = node["Facility"]
        shape = shape_map.get(fac, "circle")
        draw_custom_marker(ax, x, y, shape, color=color, size=size, edge_color='black', linewidth=2)

    legend_patches = []
    legend_order = [
        "Intersection node", "Gate Station", "Regulator Station",
        "Elevated Tank", "Pumping Station", "12kv Substation", "23kv Substation"
    ]

    for fac in legend_order:
        shape = shape_map.get(fac, "circle")
        patch = create_legend_patch(shape, INFRA_COLORS[infra_type], fac)
        legend_patches.append(patch)

    ax.legend(handles=legend_patches, frameon=True, fontsize=10, loc='best', prop={'family': 'Times New Roman'})

    ax.set_aspect('equal')
    plt.grid(False)
    plt.tight_layout()
    plt.show()

# 绘制三类基础设施网络
for itype in ["gas", "water", "power"]:
    plot_network_by_type(itype, nodes, edges, areas, region, point_size=350, line_width=4)