# Emoji Generation Strategy

Advanced patterns for semantic emoji matching based on prompt descriptions.

## Core Semantic Categories

### Business & Management

| Keywords | Emoji | Rationale |
|----------|-------|-----------|
| product manager, PM, business, strategy, roadmap | 👨‍💼 | Business professional |
| executive, CEO, leadership, management | 👔 | Executive/leadership |
| marketing, growth, branding | 📢 | Announcement/promotion |
| sales, customer, account | 🤝 | Handshake/deal |
| startup, founder, entrepreneur | 🚀 | Launch/growth |

### Development & Technology

| Keywords | Emoji | Rationale |
|----------|-------|-----------|
| developer, engineer, coding, programming, code | 👨‍💻 | Technical work |
| frontend, UI, web, HTML, CSS | 🌐 | Web/internet |
| backend, API, server, database | ⚙️ | Gears/system |
| mobile, iOS, Android, app | 📱 | Mobile device |
| DevOps, infrastructure, deployment | 🔧 | Tools/fixing |
| security, authentication, encryption | 🔒 | Security |
| debugging, troubleshooting, fix | 🐛 | Bug |

### Content & Creative

| Keywords | Emoji | Rationale |
|----------|-------|-----------|
| writer, content, copy, writing, blog | ✍️ | Writing |
| designer, creative, art, UI/UX, design | 🎨 | Art/creativity |
| video, editing, production | 🎬 | Movie production |
| photography, image | 📷 | Camera |
| music, audio, sound | 🎵 | Music note |

### Data & Analytics

| Keywords | Emoji | Rationale |
|----------|-------|-----------|
| analytics, data, metrics, analysis | 📊 | Bar chart |
| reporting, dashboard, KPI | 📈 | Increasing chart |
| research, study, investigation | 🔬 | Microscope |
| spreadsheet, Excel, table | 📋 | Clipboard |
| database, SQL, storage | 💾 | Floppy disk |

### Communication & Support

| Keywords | Emoji | Rationale |
|----------|-------|-----------|
| assistant, helper, copilot, aid, AI agent | 🤖 | Robot/AI |
| chat, support, communication, messaging | 💬 | Chat bubble |
| email, newsletter | 📧 | Email |
| documentation, docs, wiki | 📄 | Page/document |
| tutorial, guide, learning | 📚 | Books/learning |
| translation, language | 🌍 | Globe/languages |

### Finance & Legal

| Keywords | Emoji | Rationale |
|----------|-------|-----------|
| finance, money, trading, investment | 💰 | Money bag |
| accounting, bookkeeping | 🧮 | Abacus |
| legal, contract, law | ⚖️ | Scales of justice |
| tax, compliance | 📑 | Bookmark/filing |

### Science & Education

| Keywords | Emoji | Rationale |
|----------|-------|-----------|
| teacher, education, learning, tutor | 📚 | Books |
| science, research, lab, experiment | 🔬 | Microscope |
| math, calculation | ➗ | Division |
| physics, chemistry | ⚗️ | Alembic |

## Fallback Hierarchy

When generating emojis for a prompt:

1. **Primary**: Analyze description field for semantic keywords
2. **Secondary**: Analyze filename for clues
3. **Tertiary**: Scan content body for domain-specific terms
4. **Default**: Use 🔧 (generic tool)

## Special Cases

### Multi-Domain Descriptions

If description contains multiple domain keywords:
- Choose the **most prominent** domain
- Example: "Developer and writer" → 👨‍💻 (development takes precedence)

### Action-Oriented Descriptions

| Description Pattern | Emoji |
|---------------------|-------|
| "Helps with...", "Assists in..." | 🤖 |
| "Analyzes...", "Reviews..." | 📊 |
| "Creates...", "Designs..." | 🎨 |
| "Manages...", "Leads..." | 👨‍💼 |
| "Teaches...", "Explains..." | 📚 |

### Tone-Based Selection

| Tone | Emoji |
|------|-------|
| Professional/Formal | Suit/tie emojis |
| Casual/Friendly | Smiley emojis |
| Technical | Tool/tech emojis |
| Creative | Art/color emojis |

## Testing Emoji Quality

After generating an emoji, verify:
- [ ] Emoji is relevant to the description
- [ ] Emoji renders correctly (standard Unicode)
- [ ] Emoji is a single character (not sequence)
- [ ] Emoji is appropriate for professional context
