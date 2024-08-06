from jproperties import Properties 
  
configs = Properties() 
with open('project.properties', 'rb') as read_prop: 
    configs.load(read_prop) 

print(type(configs.get('TEST').data))