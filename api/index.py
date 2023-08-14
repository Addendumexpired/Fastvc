from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, HTMLResponse
import requests

app = FastAPI()

def generate_blocks(file_content, block_size):
    offset = 0
    while offset < len(file_content):
        block = file_content[offset : offset + block_size]
        offset += block_size
        yield block



@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Stream File Example</title>
    </head>
    <body>
      <!-- Remove the button -->
      <script>
        // Automatically initiate download on page load
        window.onload = async function() {
          const response = await fetch('/stream_file');
          if (response.ok) {
            const blob = await response.blob();
            const filename = response.headers.get('content-disposition').split('filename=')[1];
            const downloadUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);
          } else {
            console.error('Request failed with status:', response.status);
          }
        };
      </script>
    </body>
    </html>
    """

@app.get("/stream_file")
async def stream_file(request: Request):
    url = "https://codeload.github.com/2dust/v2rayN/zip/refs/heads/master"  # 替换为实际的文件 URL
    block_size = 64 * 1024  # 调整块的大小

    response = requests.get(url)
    if not response.ok:
        return Response(status_code=response.status_code)

    filename =response.headers["Content-Disposition"]
    response_headers = {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": f'{filename}',  # 设置下载文件名
    }

    return StreamingResponse(
        generate_blocks(response.content, block_size),
        headers=response_headers,
        status_code=206
    )
