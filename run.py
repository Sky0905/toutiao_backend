import uvicorn


if __name__ == "__main__":
    # 直接运行本文件即可启动开发服务器，并自动监听代码变化。
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
