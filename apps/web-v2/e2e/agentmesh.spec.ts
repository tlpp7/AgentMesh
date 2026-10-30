import {test,expect} from "@playwright/test";
const token="r7-playwright-test-token-local-only-123456";
test("execute, store and replay through React -> FastAPI -> SQLite",async({page})=>{
 await page.goto("/");
 await expect(page.getByText("API connectée")).toBeVisible();
 await page.getByLabel("Objectif").fill("R7 end to end pipeline");
 await page.getByLabel("Token API (uniquement en mémoire)").fill(token);
 await page.getByRole("button",{name:"Exécuter"}).click();
 await expect(page.getByText("Accepté",{exact:true})).toBeVisible();
 await page.getByRole("button",{name:"Actualiser"}).click();
 await expect(page.getByRole("button",{name:"Rejouer"}).first()).toBeVisible();
 await page.getByRole("button",{name:"Rejouer"}).first().click();
 await expect(page.getByText(/Événements relus :/)).toBeVisible();
});
test("invalid bearer token is rejected",async({page})=>{
 await page.goto("/");
 await page.getByLabel("Token API (uniquement en mémoire)").fill("wrong-token");
 await page.getByRole("button",{name:"Exécuter"}).click();
 await expect(page.getByRole("alert")).toContainText("unauthorized");
});
test("restart-independent persisted history via API",async({request})=>{
 const headers={Authorization:"Bearer "+token};
 const r=await request.post("http://127.0.0.1:8001/api/v2/run",{headers,data:{objective:"persist R7 restart test"}});
 expect(r.ok()).toBeTruthy();
 const id=(await r.json()).run_id;
 expect(id).toBeTruthy();
 const reread=await request.get("http://127.0.0.1:8001/api/v2/runs/"+id,{headers});
 expect(reread.ok()).toBeTruthy();
});
