import {test,expect} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
test("Q05 critical and serious accessibility violations",async({page})=>{
 await page.goto("/");
 await expect(page.getByRole("main")).toBeVisible();
 const result=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]).analyze();
 const blocking=result.violations.filter(v=>v.impact==="critical"||v.impact==="serious");
 expect(blocking,JSON.stringify(blocking.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),null,2)).toEqual([]);
});
test("Q03 keyboard-accessible agent alternative",async({page})=>{
 await page.goto("/");
 const selected=page.getByRole("button",{name:/critic —/i});
 await selected.focus();
 await page.keyboard.press("Enter");
 await expect(selected).toHaveAttribute("aria-pressed","true");
 await expect(page.getByText(/Nœud sélectionné/)).toContainText("critic");
});
