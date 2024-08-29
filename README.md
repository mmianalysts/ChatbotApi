##  项目

/share/all/ds/chatbot_api

## 运行环境

1. 服务器：ssh webserver23
2. 虚拟环境：source /data/venvs/gpt_api/bin/activate（专用虚拟环境，依赖变动需要及时更新requirement.txt）
3. 重启服务（目前需要ds的账号权限, dev-2上登录后ssh到ws23）: supervisorctl -c /share/all/ds/chatbot_api/chatbot_api.conf restart chatbot-api
4. 日志: /data/var/log/chatbot_api_mqy.log.stderr

> 开发测试直接激活虚拟环境后，用`uvicorn fastapi_ws:app`启动服务

接口说明：

1. gpt_openai
openai官方接口，支持输入openai模型名称，推荐使用

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/gpt_openai', 
    data=json.dumps({'text': '1+1=?', 'model':"gpt-4-1106-preview"}), 
    verify=False
)
```

2. gpt_openai2
第三方提供的接口，支持输入openai模型名称，推荐使用

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/gpt_openai2', 
    data=json.dumps({'text': '1+1=?', 'model':"gpt-4-1106-preview"}), 
    verify=False
)
```

3. chatbot
gpt3.5

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/chatbot', 
    data=json.dumps({'text': '1+1=?', 'OPENAI_API_KEY':""}), 
    verify=False
)
```

4. gpt4
gpt4

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/gpt4', 
    data=json.dumps({'text': '1+1=?', 'OPENAI_API_KEY':""}), 
    verify=False
)
```

5. vec
向量化

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/vec', 
    data=json.dumps({'text': '可乐', 'OPENAI_API_KEY':""}), 
    verify=False
)
```
