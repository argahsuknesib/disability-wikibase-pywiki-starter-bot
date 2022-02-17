import enum
# Using enum class create enumerations
class Schema_key(enum.Enum):
   Entity = 'entity'
   Ignore = 'ignore'
   Relation = 'relation'
   Subject = 'subject'
   Predicate = 'predicate'
   Object= 'object'
   Column = 'column'
   Source = 'source'