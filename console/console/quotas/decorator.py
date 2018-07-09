from .tasks import sync_quota


def synchronize_quota_decorator(resource_type):

    def handle_func(func):
        def handle_args(view_ins, request, *args, **kwargs):

            payload = {
                'owner': request.data['owner'],
                'zone': request.data['zone'],
            }
            sync_quota(resource_type, payload)

            resp = func(view_ins, request, *args, **kwargs)
            return resp

        return handle_args
    return handle_func
