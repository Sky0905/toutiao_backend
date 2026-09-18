from typing import Annotated

from fastapi import Query


# 使用 Annotated 将分页校验规则直接声明在接口参数类型中。
# page 必须 >= 1，且限制最大页码，避免异常大的分页请求。
Page = Annotated[int, Query(ge=1, le=1000)]
# page_size 必须在 1 到 100 之间，避免一次查询返回过多数据。
PageSize = Annotated[int, Query(ge=1, le=100)]


def offset(page: int, page_size: int) -> int:
    # 第 1 页从第 0 条开始，第 2 页跳过一页数据。
    return (page - 1) * page_size
