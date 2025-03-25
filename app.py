import asyncio
from playwright.async_api import async_playwright
import configparser
import json
import os
from datetime import datetime
import random
import time
import logging
from typing import Dict, List, Optional
import threading
import queue
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ticket_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class TicketBot:
    def __init__(self, config: configparser.ConfigParser, status_dict: Dict):
        self.config = config
        self.status = status_dict
        self.browsers = []
        self.contexts = []
        self.pages = []
        self.stop_event = threading.Event()
        self.success_queue = queue.Queue()
        self.logger = logging.getLogger(__name__)

    async def init_browser(self, instance_id: int) -> None:
        """Initialize a browser instance with anti-detection measures"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=IsolateOrigins',
                '--disable-site-isolation-for-policy'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            java_script_enabled=True,
            bypass_csp=True,
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
        )
        
        # Add stealth scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        page = await context.new_page()
        
        # Add random mouse movements
        await page.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        self.browsers.append(browser)
        self.contexts.append(context)
        self.pages.append(page)
        self.logger.info(f"Browser instance {instance_id} initialized successfully")

    async def load_cookies(self, page, instance_id: int) -> bool:
        """Load cookies with retry mechanism"""
        retry_count = int(self.config['General']['retry_count'])
        retry_delay = float(self.config['General']['retry_delay'])
        
        for attempt in range(retry_count):
            try:
                if os.path.exists('cookies.json'):
                    with open('cookies.json', 'r') as f:
                        cookies = json.load(f)
                    await page.context.add_cookies(cookies)
                    self.logger.info(f"Instance {instance_id}: Cookies loaded successfully")
                    return True
                else:
                    self.logger.warning(f"Instance {instance_id}: No cookies file found")
                    return False
            except Exception as e:
                self.logger.error(f"Instance {instance_id}: Failed to load cookies (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    return False

    async def wait_for_sale_time(self, instance_id: int) -> None:
        """Wait for sale time with precise timing"""
        sale_time = datetime.strptime(self.config['General']['sale_time'], '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        
        if current_time >= sale_time:
            self.logger.warning(f"Instance {instance_id}: Sale time has already passed")
            return
        
        wait_time = (sale_time - current_time).total_seconds()
        self.logger.info(f"Instance {instance_id}: Waiting {wait_time:.2f} seconds until sale time")
        
        # Precise waiting
        while wait_time > 0 and not self.stop_event.is_set():
            if wait_time > 1:
                await asyncio.sleep(1)
                wait_time -= 1
            else:
                await asyncio.sleep(wait_time)
                wait_time = 0

    async def click_with_retry(self, page, selector: str, instance_id: int, max_retries: int = 3) -> bool:
        """Click element with retry mechanism and random delay"""
        for attempt in range(max_retries):
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    # Add random delay before clicking
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    await element.click()
                    self.logger.info(f"Instance {instance_id}: Successfully clicked {selector}")
                    return True
            except Exception as e:
                self.logger.error(f"Instance {instance_id}: Failed to click {selector} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                else:
                    return False
        return False

    async def select_ticket_category(self, page, instance_id: int) -> bool:
        """Select ticket category with smart retry"""
        categories = self.config['Tickets']['categories'].split(',')
        for category in categories:
            try:
                # Try different selectors
                selectors = [
                    f"text={category}",
                    f"//div[contains(text(), '{category}')]",
                    f"//span[contains(text(), '{category}')]"
                ]
                
                for selector in selectors:
                    if await self.click_with_retry(page, selector, instance_id):
                        return True
                
                # If no exact match, try partial match
                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        await elements[0].click()
                        self.logger.info(f"Instance {instance_id}: Selected category {category}")
                        return True
                
            except Exception as e:
                self.logger.error(f"Instance {instance_id}: Failed to select category {category}: {str(e)}")
                continue
        
        return False

    async def select_ticket_quantity(self, page, instance_id: int) -> bool:
        """Select ticket quantity with validation"""
        try:
            quantity = int(self.config['Tickets']['quantity'])
            if quantity < 1 or quantity > 4:
                self.logger.error(f"Instance {instance_id}: Invalid quantity {quantity}")
                return False
            
            # Try different quantity selection methods
            selectors = [
                f"//button[contains(text(), '{quantity}')]",
                f"//div[contains(text(), '{quantity}')]",
                f"//span[contains(text(), '{quantity}')]"
            ]
            
            for selector in selectors:
                if await self.click_with_retry(page, selector, instance_id):
                    return True
            
            # If no direct selector found, try increment/decrement buttons
            for _ in range(quantity - 1):
                if not await self.click_with_retry(page, "//button[contains(text(), '+')]", instance_id):
                    return False
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Instance {instance_id}: Failed to select quantity: {str(e)}")
            return False

    async def handle_checkout(self, page, instance_id: int) -> bool:
        """Handle checkout process with payment selection"""
        try:
            # Wait for checkout page to load
            await page.wait_for_load_state('networkidle')
            
            # Select manual payment
            payment_selectors = [
                "//div[contains(text(), 'Manual Payment')]",
                "//span[contains(text(), 'Manual Payment')]",
                "//button[contains(text(), 'Manual Payment')]"
            ]
            
            for selector in payment_selectors:
                if await self.click_with_retry(page, selector, instance_id):
                    break
            
            # Wait for confirmation
            await page.wait_for_timeout(2000)
            
            # Check for success indicators
            success_indicators = [
                "//div[contains(text(), 'Order Confirmed')]",
                "//span[contains(text(), 'Success')]",
                "//div[contains(text(), 'Payment Successful')]"
            ]
            
            for indicator in success_indicators:
                try:
                    element = await page.wait_for_selector(indicator, timeout=5000)
                    if element:
                        self.logger.info(f"Instance {instance_id}: Order confirmed successfully")
                        self.success_queue.put(True)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Instance {instance_id}: Checkout failed: {str(e)}")
            return False

    async def run_instance(self, instance_id: int) -> None:
        """Run a single browser instance"""
        try:
            page = self.pages[instance_id]
            url = self.config['General']['url']
            
            # Load cookies
            if not await self.load_cookies(page, instance_id):
                self.logger.error(f"Instance {instance_id}: Failed to load cookies, stopping instance")
                return
            
            # Navigate to URL
            await page.goto(url, wait_until='networkidle')
            self.logger.info(f"Instance {instance_id}: Navigated to {url}")
            
            # Wait for sale time
            await self.wait_for_sale_time(instance_id)
            
            if self.stop_event.is_set():
                return
            
            # Start purchase process
            retry_count = int(self.config['General']['retry_count'])
            for attempt in range(retry_count):
                if self.stop_event.is_set():
                    return
                
                self.logger.info(f"Instance {instance_id}: Attempt {attempt + 1}/{retry_count}")
                
                # Refresh page
                await page.reload(wait_until='networkidle')
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Click buttons in sequence
                button_sequence = [
                    "//button[contains(text(), 'Buy Now')]",
                    "//button[contains(text(), 'Select')]",
                    "//button[contains(text(), 'Confirm')]"
                ]
                
                success = True
                for button in button_sequence:
                    if not await self.click_with_retry(page, button, instance_id):
                        success = False
                        break
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                
                if not success:
                    continue
                
                # Select ticket category
                if not await self.select_ticket_category(page, instance_id):
                    continue
                
                # Select quantity
                if not await self.select_ticket_quantity(page, instance_id):
                    continue
                
                # Handle checkout
                if await self.handle_checkout(page, instance_id):
                    self.status['success'] = True
                    self.status['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    return
            
            self.logger.warning(f"Instance {instance_id}: All attempts failed")
            
        except Exception as e:
            self.logger.error(f"Instance {instance_id}: Error during execution: {str(e)}")
        finally:
            self.status['instances'] -= 1
            if self.status['instances'] == 0:
                self.status['running'] = False
                self.status['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    async def cleanup(self) -> None:
        """Cleanup browser instances"""
        for context in self.contexts:
            await context.close()
        for browser in self.browsers:
            await browser.close()
        self.browsers.clear()
        self.contexts.clear()
        self.pages.clear()

    async def run(self) -> None:
        """Main execution method"""
        try:
            num_instances = int(self.config['General']['browser_instances'])
            self.status['instances'] = num_instances
            self.status['running'] = True
            self.status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Initialize browsers
            for i in range(num_instances):
                await self.init_browser(i)
            
            # Run instances concurrently
            tasks = [self.run_instance(i) for i in range(num_instances)]
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.error(f"Error in main execution: {str(e)}")
        finally:
            await self.cleanup()

def start_bot(status_dict: Dict) -> None:
    """Start the ticket bot"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    bot = TicketBot(config, status_dict)
    asyncio.run(bot.run())

def stop_bot() -> None:
    """Stop the ticket bot"""
    if hasattr(stop_bot, 'bot'):
        stop_bot.bot.stop_event.set()

if __name__ == "__main__":
    status_dict = {
        "running": False,
        "start_time": None,
        "instances": 0,
        "success": False,
        "last_update": None
    }
    start_bot(status_dict)
