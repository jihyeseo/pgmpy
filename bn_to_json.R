bn_dataset <- earthquake
nodes = character()
arcs_from = character()
arcs_to = character()
cpds = list()

i <- 1

for (line in bn_dataset) {
  nodes[[i]] = line$node
  nodename = nodes[[i]]
  for (child in line$children) {
    arcs_from[[length(arcs_from)+1]]  =  line$node  
    arcs_to[[length(arcs_to)+1]]  =    child 
  }
   
  cpd_dict = list()
  cpd_dict$parents = line$parents
  
  if (attr(line, "class") == "bn.fit.gnode") {
    # continuous var with continuous parents - try to get same things as existing json files
    coef_dict = list()
    for (key_name in names(line$coefficients)) {
      coef_dict[[key_name]]  = (line$coefficients)[[key_name]]
    }
    cpd_dict$coefficients = coef_dict
    cpd_dict$variance = round(line$sd ** 2 ,4)

  }
  else if (attr(line, "class") == "bn.fit.dnode")  {
    # categorial var  
    cpd_dict$prob = as.data.frame(line$prob)
  }
  else if (attr(line, "class") == "bn.fit.cgnode")  {
    # conditional gaussian, continuous variable with at least 1 categorial parent
    cpd_dict$dlevels = line$dlevels
    cpd_dict$coefficients = line$coefficients
    cpd_dict$configs = line$configs
    cpd_dict$variance = round(line$sd ** 2 ,4)
  }
 
  cpds[[nodename]] = cpd_dict
  i <- i+1
}

json_dict = list()
json_dict$nodes = nodes
json_dict$arcs= cbind(arcs_from, arcs_to)
json_dict$cpds= cpds
json_text <- toJSON(json_dict, pretty=TRUE)

write(json_text, file="eart.2.json")