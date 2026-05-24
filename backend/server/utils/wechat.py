import httpx
from server.config import get_settings

settings = get_settings()

WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


async def code2session(code: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(WX_CODE2SESSION_URL, params={
            "appid": settings.WX_APPID,
            "secret": settings.WX_SECRET,
            "js_code": code,
            "grant_type": "authorization_code",
        })
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise WechatAuthError(data.get("errmsg", "WeChat auth failed"))

    return {
        "openid": data["openid"],
        "session_key": data.get("session_key", ""),
        "unionid": data.get("unionid"),
    }


async def send_subscribe_message(
    openid: str,
    template_id: str,
    data: dict,
    page: str = "",
) -> bool:
    access_token = await _get_access_token()
    if not access_token:
        return False

    url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"
    payload = {
        "touser": openid,
        "template_id": template_id,
        "data": data,
        "page": page,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        result = resp.json()

    return result.get("errcode") == 0


async def _get_access_token() -> str | None:
    # TODO: implement access_token with caching
    return None


class WechatAuthError(Exception):
    pass