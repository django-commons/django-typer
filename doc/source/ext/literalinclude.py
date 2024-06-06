from docutils.parsers.rst import directives
from docutils.nodes import literal_block, Text
from sphinx.directives.code import LiteralInclude

class ExtendedLiteralInclude(LiteralInclude):
    """
    We extend literalinclude to allow :replace: strings to be provided. This helps
    us fix imports that may be confusing in tutorials etc.
    """

    option_spec = LiteralInclude.option_spec.copy()
    option_spec['replace'] = directives.unchanged

    def run(self):
        # Call the original run method to get the literal include content
        original_result = super().run()

        if 'replace' in self.options:
            replace_option = self.options['replace']
            replacements = self.parse_replacements(replace_option)
            if not replacements:
                return original_result

            # Modify the content in original_result
            def make_replacements(node):
                if isinstance(node, literal_block):
                    content = node.rawsource
                    for old_text, new_text in replacements.items():
                        content = content.replace(old_text, new_text)

                    node.rawsource = content
                    node.children[0] = Text(content)
                    node.children[0].parent = node

            def walk_nodes(nodes):
                for node in nodes:
                    make_replacements(node)
                    if hasattr(node, 'children'):
                        walk_nodes(node.children)
            
            walk_nodes(original_result)

        return original_result

    def parse_replacements(self, replace_option):
        replacements = {}
        lines = replace_option.splitlines()
        for line in lines:
            if ':' in line:
                old_text, new_text = line.split(':', 1)
                replacements[old_text.strip()] = new_text.strip()
        return replacements
