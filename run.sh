#!/bin/bash
container_name=chatbot_api

if [ "$(docker ps -aqf name=$container_name)" ]; then
    docker stop $container_name
    docker rm $container_name
fi

docker run \
    -dit \
    --restart=always \
    --name chatbot_api \
    --network host \
    -e PORT=14883 \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -e AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
    -e ARK_API_KEY=$ARK_API_KEY \
    -e DPSK_API_KEY=$DPSK_API_KEY \
    -e CLAUDE_API_KEY=$CLAUDE_API_KEY \
    -e MINIMAX_API_KEY=$MINIMAX_API_KEY \
    -e VOLC_ACCESSKEY=$VOLC_ACCESSKEY \
    -e VOLC_SECRETKEY=$VOLC_SECRETKEY \
    -e SG_PROXY_USER=$SG_PROXY_USER \
    -e SG_PROXY_PASSWD=$SG_PROXY_PASSWD \
    -v $(pwd):/app \
    -v /data/var/log:/data/var/log \
    moojing-reg.tencentcloudcr.com/data-science/chatbot_api:v0