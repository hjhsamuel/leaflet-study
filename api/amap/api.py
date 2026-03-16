from typing import Tuple, Optional, List
from urllib.parse import urljoin

import requests

from api.amap import schema


class AMap:
    def __init__(self, addr: str, key: str):
        self._addr = addr
        self._cred = key

    def regeo(self, loc: schema.Location) -> Tuple[Optional[schema.ReGeoCode], Optional[Exception]]:
        path = urljoin(self._addr, "/v3/geocode/regeo")
        params = {
            'key': self._cred,
            'location': '%.6f,%.6f' % (loc.lng, loc.lat),
            'extensions': 'base',
        }

        # proxy
        # TODO
        proxy = {'http': '', 'https': ''}

        rsp = requests.get(path, params, timeout=5, proxies=proxy, verify=False)
        try:
            info = schema.ReGeoRsp(**rsp.json())
        except Exception as e:
            return None, e

        if info.status != "1":
            return None, Exception(info.info)
        return info.regeocode, None

    def get_road_info(self, loc: schema.Location) -> Tuple[str, Optional[Exception]]:
        info, e = self.regeo(loc)
        if e:
            return '', e
        if info.addressComponent is None:
            return '', Exception('unknown address component')
        res = []
        if info.addressComponent.province:
            res.append(info.addressComponent.province)
        if info.addressComponent.city:
            res.append(info.addressComponent.city)
        if info.addressComponent.district:
            res.append(info.addressComponent.district)
        if info.addressComponent.streetNumber:
            res.append(info.addressComponent.streetNumber.street)
            res.append(info.addressComponent.streetNumber.number)
        return '-'.join(res), None

    def driving(self, req: schema.DrivingReq) -> Tuple[int, Optional[schema.DrivingRoute], Optional[Exception]]:
        path = urljoin(self._addr, '/v5/direction/driving')
        params = {
            'key': self._cred,
            'origin': '%.6f,%.6f' % (req.origin.lng, req.origin.lat),
            'destination': '%.6f,%.6f' % (req.dest.lng, req.dest.lat),
            'show_fields': 'polyline'
        }
        if req.waypoints and len(req.waypoints):
            # 最大支持16个途径点
            if len(req.waypoints) > 16:
                return 0, None, Exception('too many waypoints')
            waypoints = []
            for waypoint in req.waypoints:
                waypoints.append('%.6f,%.6f' % (waypoint.lng, waypoint.lat))
            params['waypoints'] = ';'.join(waypoints)

        # proxy
        # TODO
        proxy = {'http': '', 'https': ''}

        rsp = requests.post(path, params, timeout=5, proxies=proxy, verify=False)
        try:
            info = schema.DrivingRsp(**rsp.json())
            if info.status != "1" or info.infocode != "10000":
                return 0, None, Exception(info.info)
            cnt = int(info.count)
        except Exception as e:
            return 0, None, e
        return cnt, info.route, None

    def poi(self, key: str) -> Tuple[Optional[schema.POIRsp], Optional[Exception]]:
        path = urljoin(self._addr, '/v5/place/text')
        params = {
            'key': self._cred,
            'keywords': key
        }

        # proxy
        # TODO
        proxy = {'http': '', 'https': ''}

        rsp = requests.get(path, params, timeout=5, proxies=proxy, verify=False)
        try:
            out = rsp.json()
            info = schema.POIRsp(**out)
            if info.status != "1" or info.infocode != "10000":
                return None, Exception(info.info)
        except Exception as e:
            return None, e
        return info, None






