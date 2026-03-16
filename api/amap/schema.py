from dataclasses import dataclass
from typing import Optional, List, Union

from pydantic import BaseModel


class StreetInfo(BaseModel):
    street: Union[str, List]  # 街道名称
    number: Union[str, List]  # 门牌号
    location: Union[str, List, None]  # 坐标点
    direction: Union[str, List]  # 方向，坐标点所处街道方位，经纬度坐标点：经度，纬度
    distance: Union[str, List]  # 门牌地址到请求坐标的距离，单位：米


class BusinessAreaInfo(BaseModel):
    businessArea: Optional[str]  # 商圈信息
    location: Optional[str]  # 商圈中心点经纬度
    name: Optional[str]  # 商圈名称，例如：颐和园
    id: Optional[str]  # 商圈所在区域的 adcode，例如：朝阳区/海淀区


class RoadInfo(BaseModel):
    id: str  # 道路 id
    name: str  # 道路名称
    distance: str  # 道路到请求坐标的距离，单位：米
    direction: str  # 方位，输入点和此路的相对方位
    location: str  # 坐标点


class RoadinterInfo(BaseModel):
    distance: str  # 交叉路口到请求坐标的距离, 单位：米
    direction: str  # 方位, 输入点相对路口的方位
    location: str  # 路口经纬度
    first_id: str  # 第一条道路 id
    first_name: str  # 第一条道路名称
    second_id: str  # 第二条道路 id
    second_name: str  # 第二条道路名称


class AddressComponent(BaseModel):
    country: str  # 所在国家名称
    province: str  # 所在省名称
    city: Optional[str]  # 所在城市名称，当城市是省直辖县时返回为空
    citycode: str  # 城市编码
    district: str  # 所在区
    adcode: str  # 行政区编码
    township: str  # 所在乡镇/街道（此街道为社区街道，不是道路信息）
    towncode: str  # 乡镇街道编码
    streetNumber: Optional[StreetInfo]  # 门牌信息列表
    businessAreas: Optional[List[BusinessAreaInfo]]  # 经纬度所属商圈列表


class ReGeoCode(BaseModel):
    addressComponent: Optional[AddressComponent]
    roads: Optional[List[RoadInfo]]  # 道路信息列表
    roadinters: Optional[List[RoadinterInfo]]  # 道路交叉口列表


class ReGeoRsp(BaseModel):
    status: str  # 0: 失败，1：成功
    info: str  # 具体错误信息，成功时返回 'OK'
    regeocode: Optional[ReGeoCode]  # 逆地理编码列表


@dataclass
class Location:
    lng: float
    lat: float


class DrivingReq(BaseModel):
    origin: Location  # 起点
    dest: Location  # 终点
    waypoints: Optional[List[Location]]  # 途径点，最多16个


class DrivingPathStep(BaseModel):
    instruction: str  # 行驶指示
    orientation: str  # 进入道路方向
    road_name: Optional[str]  # 分段道路名称
    step_distance: str  # 分段距离信息
    polyline: str  # 设置后可返回分路段坐标点串，两点间用“;”分隔


class DrivingPathInfo(BaseModel):
    distance: str  # 方案距离，单位：米
    restriction: str  # 0: 限行已规避或未限行，即该路线没有限行路段; 1: 限行无法规避，即该线路有限行路段
    steps: Optional[List[DrivingPathStep]]  # 路线分段


class DrivingRoute(BaseModel):
    origin: str  # 起点经纬度
    destination: str  # 终点经纬度
    paths: Optional[List[DrivingPathInfo]]  # 算路方案详情


class DrivingRsp(BaseModel):
    status: str  # 0: 失败，1：成功
    info: str  # 具体错误信息，成功时返回 'OK'
    infocode: str  # 返回状态说明,10000代表正确
    count: str  # 路径规划方案总数
    route: Optional[DrivingRoute]  # 规划方案列表


class POIInfo(BaseModel):
    name: str  # 名称
    id: str  # 唯一标识
    parent: Optional[str]  # POI 的 ID，当前 POI 如果有父 POI，则返回父 POI 的 ID。可能为空
    distance: Optional[str]  # 离中心点距离，单位米；仅在周边搜索的时候有值返回
    location: str  # 经纬度
    type: str  # 所属类型
    typecode: str  # 分类编码
    pname: str  # 所属省份
    cityname: str  # 所属城市
    adname: str  # 所属区县
    address: str  # 详细地址
    pcode: str  # 所属省份编码
    adcode: str  # 所属区域编码
    citycode: str  # 所属城市编码


class POIRsp(BaseModel):
    status: str
    info: str
    infocode: str
    count: str
    pois: List[POIInfo] = None
