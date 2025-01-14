"""
This script processes the output of sphinxbuild -d linkcheck to find broken links. It will pretty
print broken links to stderr and return a non-zero exit code if any broken links are found.
"""

import sys
import json
from pathlib import Path

if __name__ == "__main__":
    
    # The json output isn't valid, so we have to fix it before we can process.
    data = json.loads(f"[{','.join((Path(__file__).parent / 'build/output.json').read_text().splitlines())}]")
    broken_links = [link for link in data if link["status"] not in {"working", "redirected", "unchecked", "ignored"}]
    if broken_links:
        for link in broken_links:
            print(f"[{link['status']}] {link['filename']}:{link['lineno']} -> {link['uri']}", file=sys.stderr)
        sys.exit(1)
