import json
from docx import Document


def tool_graph_to_chunks(input_json_file):
    """
    Processes the tool relationship data from 'tool_relationship.json' and generates
    a Word document ('tool_description04.docx') containing the tool relationships, formatted as chains.
    """

    # Define the input and output files directly within the function
    input_json_file = 'tool_relationship_version_R2.json'  # Input JSON file with tool relationships
    output_doc_file = 'tool_chunks_version_R2.docx'  # Output DOCX file

    # Load the tool relationship data from the provided JSON file
    with open(input_json_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    # Create a new Document object
    doc = Document()

    # Helper function to add a relationship chain to the document with numbering
    def add_relationship_chain_to_doc(chain, chain_number):
        chain_str = " ".join(chain)
        doc.add_paragraph(f"{chain_number}. {chain_str}")

    # Process the JSON data and find relationships between tools
    relationships = []

    # First, process the "provides_input_to" relationships for 2 tools
    for item in data:
        start_tool = item["p"]["start"]["properties"]["name"]
        end_tool = item["p"]["end"]["properties"]["name"]
        relationship = "provides_input_to"

        # Add the 2-tool relationship to the list
        relationships.append((start_tool, relationship, end_tool))

    # Function to build the relationship chain for 3 or more tools
    def build_tool_chain(relationships):
        chain_list = []
        # Start by adding the 2-tool relationships
        for start_tool, _, end_tool in relationships:
            chain_list.append([start_tool, relationship, end_tool])

        # Extend the chain to 3-tool relationships and beyond
        max_chain_length = 5  # You can increase this to 6, 7, etc. if needed

        for length in range(3, max_chain_length + 1):
            new_chains = []
            for chain in chain_list:
                last_tool = chain[-1]
                for start_tool, _, end_tool in relationships:
                    if last_tool == start_tool:
                        new_chain = chain + [relationship, end_tool]
                        new_chains.append(new_chain)
            chain_list.extend(new_chains)

        return chain_list

    # Build the tool chains for 3 or more tools
    tool_chains = build_tool_chain(relationships)

    # Output each chain with a number
    for idx, chain in enumerate(tool_chains, 1):
        add_relationship_chain_to_doc(chain, idx)

    # Save the generated document to the specified output file
    doc.save(output_doc_file)

    print(f"Document saved as {output_doc_file}")

tool_graph_to_chunks('input_json_file')