import enum
# Using enum class create enumerations
class PropertyDataType(enum.Enum):
   WikiItem = 'wikibase-item'
   String = 'string'
   Quantity = 'quantity'
   Time = 'time'
   URL = 'url'
   ExternalId= 'external-id'