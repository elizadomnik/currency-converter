const { Given, When, Then } = require("@cucumber/cucumber");
const { expect } = require("chai");

Given("I am on the currency dashboard", async function () {
  try {
    await this.page.goto("http://localhost:4200", {
      waitUntil: "networkidle0",
    });
  } catch (e) {
    console.error(
      "Error: Could not connect to http://localhost:4200. Ensure the Angular app is running (npm start).",
    );
    throw e;
  }
});

Then("I should see the {string} title", async function (expectedTitle) {
  const element = await this.page.waitForSelector("mat-card-title", {
    timeout: 5000,
  });

  const actualTitle = await this.page.evaluate((el) => el.textContent, element);
  expect(actualTitle).to.contain(expectedTitle);
});

When("I enter the date {string}", async function (dateStr) {
  const inputSelector = "input[matInput]";
  await this.page.waitForSelector(inputSelector);

  const input = await this.page.$(inputSelector);
  await input.click({ clickCount: 3 });
  await input.press("Backspace");

  await input.type(dateStr);
  await input.press("Tab");
});

When("I click the {string} button", async function (btnText) {
  // Use Puppeteer's text selector (::-p-text) which replaces XPath in newer versions
  const selector = `button ::-p-text(${btnText})`;
  try {
    const button = await this.page.waitForSelector(selector, { timeout: 5000 });
    if (button) {
      await button.click();
    } else {
      throw new Error(`Button with text "${btnText}" not found`);
    }
  } catch (e) {
    throw new Error(`Failed to click button "${btnText}": ${e.message}`);
  }
});

Then("I should see the currency rates table", async function () {
  const table = await this.page.waitForSelector("table[mat-table]", {
    timeout: 10000,
  });
  expect(table).to.exist;

  const rows = await this.page.$$("tr[mat-row]");
  expect(rows.length).to.be.at.least(1);
});