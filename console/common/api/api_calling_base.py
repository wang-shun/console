from console.common.api.osapi import api


def base_prepared(params, payload, optional_params, **kwargs):
    owner = params.get("owner", None)
    zone = params.get("zone", None)
    assert owner, "owner is None"
    assert zone, "zone is None"
    payload.update({
        "owner": owner,
        "zone": zone
    })
    for k in optional_params:
        if k in kwargs:
            payload.update({k: kwargs.get(k)})
            kwargs.pop(k, None)
    for k, v in params.items():
        if k in optional_params and k not in payload.keys():
            payload.update({k: v})
    return payload, kwargs


def base_get_api_calling(params, payload, optional_params, **kwargs):
    payload, kwargs = base_prepared(params, payload, optional_params, **kwargs)
    resp = api.get(payload=payload, **kwargs)
    return resp


def base_post_api_calling(dataparams, params, payload, optional_params, **kwargs):
    payload, kwargs = base_prepared(params, payload, optional_params, **kwargs)
    urlparams = []
    for k in dict(payload).keys():
        if k not in dataparams:
            urlparams.append(k)
    resp = api.post(payload=payload, urlparams=urlparams, **kwargs)
    return resp
