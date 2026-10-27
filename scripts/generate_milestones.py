import urllib.request, json, os, datetime

token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

query = '''
query {
  user(login: "OP-88") {
    createdAt
    repositories(first: 100, ownerAffiliations: OWNER) {
      totalCount
      nodes {
        stargazerCount
        isFork
      }
    }
    followers { totalCount }
    pullRequests(first: 1) { totalCount }
    issues(first: 1) { totalCount }
    contributionsCollection {
      totalCommitContributions
    }
  }
}
'''

headers = {"User-Agent": "Mozilla/5.0"}
if token:
    headers["Authorization"] = f"bearer {token}"

req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query}).encode(), headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())["data"]["user"]

commits = data["contributionsCollection"]["totalCommitContributions"]
followers = data["followers"]["totalCount"]
prs = data["pullRequests"]["totalCount"]
issues = data["issues"]["totalCount"]
repos = data["repositories"]["totalCount"]
stars = sum(n["stargazerCount"] for n in data["repositories"]["nodes"] if not n["isFork"])

created = datetime.datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
now = datetime.datetime.now(datetime.timezone.utc)
days_active = (now - created).days
years_active = days_active / 365.25

cards = [
    {
        "category": "Commits",
        "rank": "Master Committer" if commits > 1000 else "Hyper Committer",
        "value": f"{commits:,}",
        "percent": min(100, int((commits / 2500) * 100)),
        "icon": '<path d="M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5h-3.32zM8 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"/>'
    },
    {
        "category": "Followers",
        "rank": "Network Anchor" if followers > 200 else "Community Member",
        "value": f"{followers}",
        "percent": min(100, int((followers / 500) * 100)),
        "icon": '<path d="M5.5 3.5a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM2 5.5a3.5 3.5 0 1 1 5.898 2.549 5.508 5.508 0 0 1 3.034 4.084.75.75 0 1 1-1.482.235 4.002 4.002 0 0 0-7.898 0 .75.75 0 0 1-1.482-.236A5.507 5.507 0 0 1 3.102 8.05 3.493 3.493 0 0 1 2 5.5z"/>'
    },
    {
        "category": "Repositories",
        "rank": "System Architect",
        "value": f"{repos}",
        "percent": min(100, int((repos / 40) * 100)),
        "icon": '<path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5v-9zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8V1.5z"/>'
    },
    {
        "category": "Stars Earned",
        "rank": "Rising Signal",
        "value": f"{stars} Stars",
        "percent": min(100, int((stars / 50) * 100)),
        "icon": '<path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25z"/>'
    },
    {
        "category": "Pull Requests",
        "rank": "Code Contributor",
        "value": f"{prs} PRs",
        "percent": min(100, int((prs / 20) * 100)),
        "icon": '<path d="M7.177 3.073L9.573.677A.25.25 0 0 1 10 .854v4.792a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354zM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5zm-2.25.75a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25zM11 2.5h-1V4h1a1 1 0 0 1 1 1v4.75a2.25 2.25 0 1 1-1.5 0V6a2.5 2.5 0 0 0-2.5-2.5z"/>'
    },
    {
        "category": "Tenure",
        "rank": f"{years_active:.1f} Years Active",
        "value": f"{days_active} Days",
        "percent": min(100, int((days_active / 1000) * 100)),
        "icon": '<path d="M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0zm.75 4.75a.75.75 0 0 0-1.5 0v3.5a.75.75 0 0 0 .37.65l2.5 1.5a.75.75 0 1 0 .76-1.3L8.75 7.88V4.75z"/>'
    }
]

svg_width = 820
svg_height = 230
cols = 3
card_w = 256
card_h = 95
gap_x = 14
gap_y = 14
start_x = 12
start_y = 12

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #0d1117; }}
    .card {{ fill: #161b22; stroke: #30363d; stroke-width: 1px; rx: 8px; }}
    .cat-title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11px; fill: #8b949e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
    .rank-title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 13px; fill: #02d2d3; font-weight: 700; }}
    .val-text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 12px; fill: #c9d1d9; font-weight: 500; }}
    .rank-lbl {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 9px; fill: #8b949e; font-weight: 600; letter-spacing: 0.5px; }}
    .bar-bg {{ fill: #21262d; rx: 2.5px; }}
    .bar-fill {{ fill: #02d2d3; rx: 2.5px; }}
    .icon {{ fill: #02d2d3; }}
  </style>
  <rect width="{svg_width}" height="{svg_height}" class="bg" rx="10"/>
'''

for i, card in enumerate(cards):
    r = i // cols
    c = i % cols
    x = start_x + c * (card_w + gap_x)
    y = start_y + r * (card_h + gap_y)
    
    svg += f'''
  <g transform="translate({x}, {y})">
    <rect width="{card_w}" height="{card_h}" class="card"/>
    <g transform="translate(14, 12)" class="icon">
      {card["icon"]}
    </g>
    <text x="38" y="24" class="cat-title">{card["category"]}</text>
    <text x="14" y="48" class="rank-title">{card["rank"]}</text>
    <text x="14" y="65" class="val-text">{card["value"]}</text>
    
    <!-- Progress bar -->
    <text x="14" y="82" class="rank-lbl">RANK</text>
    <rect x="44" y="75" width="160" height="5" class="bar-bg"/>
    <rect x="44" y="75" width="{int(160 * (card["percent"] / 100))}" height="5" class="bar-fill"/>
    <text x="212" y="82" class="rank-lbl">{card["percent"]}%</text>
  </g>
'''

svg += '</svg>'

out_path = os.path.join(os.path.dirname(__file__), "..", "milestones.svg")
with open(out_path, "w") as f:
    f.write(svg)

print(f"Generated {out_path} successfully!")
