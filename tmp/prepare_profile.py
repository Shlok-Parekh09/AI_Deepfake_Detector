from pathlib import Path
import shutil
import base64

base = Path(__file__).resolve().parent
src = base / 'profile-readme'
dst = base / 'shlok-profile'
dst.mkdir(exist_ok=True)
for folder in ['scripts', '.github']:
    shutil.copytree(src / folder, dst / folder, dirs_exist_ok=True)
for folder in ['assets', 'ctf', 'stars']:
    (dst / folder).mkdir(exist_ok=True)
shutil.copy(src / '.gitignore', dst / '.gitignore')
for p in (dst / 'scripts').rglob('*.py'):
    text = p.read_text(encoding='utf-8').replace('Kaushik2210', 'Shlok-Parekh09').replace('Swas00', 'Shlok-Parekh09')
    if p.name == 'banners.py':
        text = text.replace('NAME = "Swastik"', 'NAME = "Shlok"').replace('Full-stack software developer.', 'Building with Agentic AI.').replace('Exploring GenAI, LLMs & LangChain.', 'Exploring AI & Cybersecurity.').replace('MCA student & passionate builder.', '3rd-year B.Tech CSE student.').replace('FULL-STACK  &#183;  AI &amp; GENAI', 'AGENTIC AI  &#183;  CYBERSECURITY')
    if p.name == 'common.py':
        text = text.replace('createdAt followers', 'databaseId createdAt followers')
    if p.name == 'dossier.py':
        text = text.replace('CROP = (0.20, 0.40, 0.82, 1.0)', 'CROP = (0.0, 0.0, 1.0, 1.0)').replace('Full-Stack Dev / AI', 'Agentic AI / Security').replace('u["id"] if "id" in u else "83902056"', 'u["databaseId"]').replace('font-size="21"', 'font-size="17"').replace('99.7%', 'VERIFIED').replace('MATCH <tspan', 'AVATAR <tspan').replace('ONLINE</tspan>', 'PUBLIC</tspan>')
    p.write_text(text, encoding='utf-8')
readme = (src / 'README.md').read_text(encoding='utf-8')
readme = readme.replace('Swas00', 'Shlok-Parekh09').replace('Swastik', 'Shlok').replace('SWASTIK', 'SHLOK')
readme = readme.replace('https://portfolio-swastik-sahu.vercel.app/', 'https://shlok-portfolio.pages.dev/')
readme = readme.replace('<a href="https://www.linkedin.com/in/swastik-sahu-linkdin07/">LinkedIn</a> &nbsp;·&nbsp; ', '')
readme = readme.replace('swastiks014@gmail.com', 'shlokparekh08@gmail.com')
readme = readme.replace('Shlok: full-stack developer and AI explorer. Online, last push today, 4 day streak.', 'Shlok Parekh: B.Tech CSE student exploring Agentic AI and Cybersecurity, with live GitHub activity.')
readme = readme.replace('Height is commits', 'Height is contributions').replace('taller means more commits', 'taller means more contributions')
readme = readme.replace('Everything you need is in this repo and my other repos\' names.', 'Everything you need is in this repo and the names of my AI repositories.')
readme = readme.replace('Every chart above is generated', 'Visual design and generators adapted from <a href="https://github.com/Swas00/Swas00">Swas00</a>.<br/>Every chart above is generated')
readme = readme.replace('py,js,ts,react,nextjs,nodejs,express,tailwind,docker,git,github,vscode,c,cpp,java,mongodb,postgres,postman', 'py,js,ts,react,nodejs,tailwind,docker,git,github,vscode,cloudflare')
readme = readme.replace('Languages and tools: Python, JavaScript, TypeScript, React, Next.js, Node.js, Express, Tailwind CSS, Docker, Git, GitHub, VS Code, C, C++, Java, MongoDB, Postgres, Postman', 'Languages and tools: Python, JavaScript, TypeScript, React, Node.js, Tailwind CSS, Docker, Git, GitHub, VS Code and Cloudflare')
start = readme.index('<img src="https://img.shields.io/badge/LangChain')
end = readme.index('<br/><br/>', start)
readme = readme[:start] + '''<img src="https://img.shields.io/badge/Agentic_AI-8A2BE2?style=for-the-badge&labelColor=08112b" alt="Exploring Agentic AI"/>
<img src="https://img.shields.io/badge/Cybersecurity-2496ED?style=for-the-badge&labelColor=08112b" alt="Exploring Cybersecurity"/>
<img src="https://img.shields.io/badge/Deepfake_Detection-1C3C3C?style=for-the-badge&labelColor=08112b" alt="Deepfake Detection"/>

''' + readme[end:]
(dst / 'README.md').write_text(readme, encoding='utf-8')
for p in (dst / '.github/ISSUE_TEMPLATE').glob('*.yml'):
    p.write_text(p.read_text(encoding='utf-8').replace('KAUSHIK{', 'SHLOK{'), encoding='utf-8')
for name in ['ctf/solvers.json', 'stars/visitors.json']:
    (dst / name).write_text('[]\n', encoding='utf-8')
# Stage two encodes a solvable Vigenere puzzle tied to the AI_* repositories.
flag, key = 'SHLOK{ag3nts_d3f3nd_th3_g4l4xy}', 'ai'
i = 0
cipher = ''
for c in flag:
    if c.isalpha():
        offset = ord('A') if c.isupper() else ord('a')
        cipher += chr((ord(c) - offset + ord(key[i % len(key)]) - 97) % 26 + offset)
        i += 1
    else:
        cipher += c
stage = 'STAGE 2/3 :: cipher=Vigenere (letters only, digits and braces pass through) key=the two-letter prefix shared by my CRM and Deepfake Detector repositories, lowercase payload=' + cipher
(dst / 'ctf/desc.hex').write_text(stage.encode().hex() + '\n', encoding='utf-8')
(dst / 'ATTRIBUTION.md').write_text('Visual design and SVG generator source adapted from https://github.com/Swas00/Swas00. Personalized for Shlok Parekh with his own public GitHub data, avatar, projects, links and challenge.\n', encoding='utf-8')
(dst / 'requirements.txt').write_text('Pillow==13.0.0\n', encoding='utf-8')
p = dst / '.github/workflows/showcase.yml'
text = p.read_text(encoding='utf-8').replace('pip install --quiet pillow', 'pip install --quiet -r requirements.txt').replace('git pull --rebase -X theirs -q', 'git pull --rebase -q')
text = text.replace('    permissions:\n', '    timeout-minutes: 10\n    permissions:\n')
p.write_text(text, encoding='utf-8')
(dst / 'SETUP_GUIDE.md').write_text('''# Shlok Parekh GitHub profile

README.md displays generated SVGs from assets/. The showcase Action refreshes all charts every six hours and on relevant pushes. It uses the repository GITHUB_TOKEN; no personal token is committed.

Render locally from scripts/ with GITHUB_TOKEN set, passing Shlok-Parekh09 and the output path to each generator. Install requirements.txt first. All contribution charts use the GitHub contribution calendar, which includes contributions beyond commits. Push charts use the public events feed, which has limited retention.

Visitor stars and the Hall of Fame are updated by issue workflows. The CTF_FLAG repository secret must match the final answer encrypted in ctf/desc.hex. Visitor and solver ledgers start empty.

The layout and generators are adapted from https://github.com/Swas00/Swas00; see ATTRIBUTION.md.
''', encoding='utf-8')
print(dst)
