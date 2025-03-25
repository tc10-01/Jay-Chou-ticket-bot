# 🎫 Jay Chou Ticket Killer

A powerful ticket purchasing bot for Jay Chou concerts with a modern web interface.

## Features

- 🎯 Multiple browser instances for increased success rate
- 🌐 Modern web interface for easy configuration
- 🔒 Advanced anti-detection measures
- ⚡ Asynchronous operation for better performance
- 📊 Real-time status monitoring
- 🔄 Smart retry mechanism
- 🍪 Cookie management
- 🎨 Beautiful and responsive UI

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```
4. Create a `config.ini` file with your settings (or use the web interface)
5. Place your `cookies.json` file in the project root (if you have one)

## Usage

1. Start the web interface:
   ```bash
   python web.py
   ```
2. Open your browser and navigate to `http://localhost:5000`
3. Configure your settings in the web interface:
   - Set the sale time
   - Enter the concert URL
   - Choose number of browser instances
   - Select ticket categories and quantity
4. Click "Start Bot" when ready
5. Monitor the status in real-time
6. Complete payment manually when tickets are secured

## Configuration

The bot can be configured through the web interface or by editing `config.ini`:

```ini
[General]
sale_time = 2025-03-24 17:52:00
url = https://shows.cityline.com/tc/2025/jaychoucarnivalinhk2025.html
browser_instances = 3
retry_count = 3
retry_delay = 1

[Tickets]
categories = CAT1 - HK$1688,VIP - HK$1988
quantity = 2
```

## Logging

Logs are saved to `ticket_bot.log` and displayed in the console.

## Security Notes

- Never share your `cookies.json` file
- Keep your browser instances reasonable to avoid detection
- Use random delays between actions
- Consider using a VPN for additional security

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 