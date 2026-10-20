from pathlib import Path
import xml.etree.ElementTree as ET
import re
import ast

p = Path(__file__).resolve().parent / 'shlok-profile'
svgs = list((p / 'assets').glob('*.svg'))
assert len(svgs) == 15
for f in svgs:
    ET.parse(f)
for f in (p / 'scripts').rglob('*.py'):
    ast.parse(f.read_text(encoding='utf-8'))
r = (p / 'README.md').read_text(encoding='utf-8')
refs = re.findall(r'src="(assets/[^"]+)', r)
assert all((p / x).is_file() for x in refs)
assert 'Swas00/scamalert' not in r
assert 'Shlok-Parekh09/AI_Deepfake_Detector' in r
assert bytes.fromhex((p / 'ctf/desc.hex').read_text()).startswith(b'STAGE 2/3')
for f in svgs:
    s = f.read_text(encoding='utf-8')
    assert all(name not in s for name in ['Swas00', 'Swastik', 'Kaushik2210'])
print('Validated 15 SVGs, Python syntax, README image references and personalized project table.')
