import {defineConfig,devices} from "@playwright/test";
export default defineConfig({
 testDir:"./e2e",
 timeout:30000,
 retries:process.env.CI?1:0,
 use:{baseURL:"http://127.0.0.1:5173",trace:"retain-on-failure",screenshot:"only-on-failure"},
 projects:[{name:"chromium",use:{...devices["Desktop Chrome"]}}],
 webServer:[
  {command:"python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8001",
   url:"http://127.0.0.1:8001/api/health",cwd:"../..",
   env:{...process.env,AGENTMESH_DB_PATH:"/tmp/agentmesh-r7-playwright.db",AGENTMESH_API_TOKEN:"r7-playwright-test-token-local-only-123456"},
   reuseExistingServer:!process.env.CI,timeout:60000},
  {command:"npm run dev",url:"http://127.0.0.1:5173",reuseExistingServer:!process.env.CI,timeout:60000}
 ]
});
