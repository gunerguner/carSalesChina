"""统一业务错误码定义。"""

# 参数校验类错误
VALIDATION_ERROR = 1001

# 鉴权 / 权限类错误
PERMISSION_DENIED = 1002

# 资源不存在
RESOURCE_NOT_FOUND = 1003

# 外部依赖/数据源错误
EXTERNAL_SOURCE_ERROR = 2001

# 数据库类错误
DATABASE_ERROR = 3001

# 未分类服务端错误
INTERNAL_ERROR = 9000
