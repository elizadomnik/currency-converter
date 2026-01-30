const { setWorldConstructor, Before, After, setDefaultTimeout } = require('@cucumber/cucumber');
const puppeteer = require('puppeteer');

setDefaultTimeout(10 * 1000);

class CustomWorld {
  async openBrowser() {
    this.browser = await puppeteer.launch({ headless: "new" });
    this.page = await this.browser.newPage();
  }

  async closeBrowser() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

setWorldConstructor(CustomWorld);

Before(async function () {
  await this.openBrowser();
});

After(async function () {
  await this.closeBrowser();
});
