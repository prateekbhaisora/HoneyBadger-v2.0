class AstWalker:
    # node represents the current node in the AST 
    # node_name represents the name of the node type to search for
    # nodes represents a list to store the found nodes
    # This is a recursive function used to traverse an abstract syntax tree (AST) and find nodes of a specific type. 
    # It recursively explores the tree structure, starting from the root node, and adds nodes of the specified type to 
    # a list called nodes, for further processing.
    def walk(self, node, node_name, nodes):
        if node["name"] and node["name"] == node_name:
            nodes.append(node)
        else:
            if "children" in node and node["children"]:
                for child in node["children"]:
                    self.walk(child, node_name, nodes)

    # def walk(self, node, node_name, nodes):
    #     if node.get("name") == node_name:
    #         nodes.append(node)
    #     else:
    #         if "children" in node and node["children"]:
    #             for child in node["children"]:
    #                 self.walk(child, node_name, nodes)
