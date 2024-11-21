# VK Bot with Plugin System and VK Cloud Integration

This repository hosts a **VK bot** built with a **plugin system** and integrated with **VK Cloud services**. The bot supports modular plugins for extended functionality, such as fetching statistics, birthday reminders, calculator operations, and more.

---

## Features
- **Modular Plugin System**: Add or remove plugins to extend bot functionality without modifying core code.
- **VK Cloud API Integration**: Seamless communication with VK services using API calls.
- **Asynchronous Processing**: Efficient message handling using asyncio.
- **Customizable Commands**: Define commands and their usage directly in plugins.
- **Logging and Debugging**: Integrated logging for monitoring bot activity.

---

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Plugin Examples](#plugin-examples)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/vkBotBase.git
   cd vk-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up VK API token**:
   - Create a `.env` file and add your VK API token:
     ```
     VK_API_TOKEN=your_vk_token_here
     ```

4. **Run the bot**:
   ```bash
   python main.py
   ```

---

## Usage
The bot listens for commands defined in the plugins. Each plugin can have its specific triggers and responses. Example:

- `счётчики`: Displays user account statistics.
- `др [группа]`: Lists upcoming birthdays in a specified group.
- `посчитать [выражение]`: Performs mathematical calculations.
- `команды`: Displays the list of available commands.
и другие
---

## Plugin Examples

### 1. **Account Statistics**
Command: `счётчики`

Fetches and displays user account counters using the VK API.

```python
from plugin_system import Plugin

plugin = Plugin('Счётчики', usage='счётчики - узнать статистику аккаунта')

@plugin.on_command('счётчики', 'статистика')
async def stats(msg, args):
    stats = await msg.vk.method('account.getCounters')
    response = '\n'.join(f'{name} = {count}' for name, count in stats.items()) or "Всё по нулям"
    await msg.answer(f"Счётчики аккаунта:\n{response}")
```

---
## Contributing
We welcome contributions! Here's how you can help:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with your changes.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
