# Slight modification of Johannes's R code
# https://stackoverflow.com/questions/25471567/how-to-prevent-read-table-from-changing-underscores-and-hyphens-to-dots

mk_consid_commit <- function(){
    library(zeallot)
    
    capacity.data.gas <- read.csv("data/gas_panel_data.csv", check.names = F)
    capacity.data.coal<- read.csv("data/coal_panel_data_CO2.csv",check.names = F)
    capacity.data.steel <- read.csv("data/steel_panel_clean.csv",check.names = F)
    capacity.data.coal.MW <- read.csv("data/coal_panel_data_MW.csv",check.names = F)

    createStream <- function(capacity.data, asset.type, var, status, years = 2021:2100){

      ## creating the container to get committed data
      #years <- 2021:2100
      considered <- as.data.frame(matrix(0,nrow=nrow(capacity.data),ncol=(length(years)+1)))
      names(considered)[1] <- "country"
      names(considered) [2:ncol(considered)] <- years
      names(considered) <- paste(asset.type,status,names(considered),sep=".")
      names(considered)[1] <- "country"
        
      considered$country <- capacity.data$country

      # outer loop -- start year of capacity data:
      for (i in 1:length(years)){
          
        # create the origin variable
        origin.variable <- paste(asset.type,var,status,years[i],sep=".")
        
        # if existing, go into deeper loop:
        if(origin.variable %in% names(capacity.data))  
        {
          # gas
          if(asset.type == "gas"){
                  lifetime <- 40
                  annual.emissions <- 1/12 / lifetime
                  variable <- "cap"
                    for (j in 1:lifetime){
                      lifetime.years <- years[i]:(years[i] +lifetime - 1)
                      target.variable <- paste(asset.type,status,lifetime.years[j], sep=".")
                      if(target.variable %in% names(considered)){
                      considered[,target.variable] <- considered[,target.variable] + capacity.data[,origin.variable] * annual.emissions}}}

          # coal -- MW data 
          if(asset.type == "coal" & var == "MW"){
            lifetime <- 40
            annual.emissions <- 1/6 /lifetime
            variable <- "MW"
            for (j in 1:lifetime){
              lifetime.years <- years[i]:(years[i] +lifetime - 1)
              target.variable <- paste(asset.type,status,lifetime.years[j], sep=".")
              if(target.variable %in% names(considered)){
                considered[,target.variable] <- considered[,target.variable] + capacity.data[,origin.variable] * annual.emissions}}}

          #coal CO2 emissions
          if(asset.type == "coal" & var == "CO2"){
            lifetime <- 40
            variable <- "CO2"
            for (j in 1:lifetime){
              lifetime.years <- years[i]:(years[i] +lifetime - 1)
              target.variable <- paste(asset.type,status,lifetime.years[j], sep=".")
              if(target.variable %in% names(considered)){
                considered[,target.variable] <- considered[,target.variable] + capacity.data[,origin.variable]}}}

          # steel emissions
          if(asset.type == "steel"){
            lifetime <- 40
            variable <- "cap"
            for (j in 1:lifetime){
              lifetime.years <- years[i]:(years[i] +lifetime - 1)
              target.variable <- paste(asset.type,status,lifetime.years[j], sep=".")
              if(target.variable %in% names(considered)){
                considered[,target.variable] <- considered[,target.variable] + capacity.data[,origin.variable]}}}}}

      return(considered)}

    print(considered)
    
    # create gas data
    gas.proposed <- createStream(capacity.data.gas,"gas","cap","proposed")
    gas.construction <- createStream(capacity.data.gas,"gas","cap","construction")
    gas.consid <- merge(gas.proposed,gas.construction,by="country",all=T)
    
    gas.operating <- createStream(capacity.data.gas,"gas","cap","operating",1937:2100)
    gas.committed <- gas.operating[,c(1,86:ncol(gas.operating))]

    # create coal data
    ## create coal data vars (CO2 & MW)
    coal.permitted <- createStream(capacity.data.coal,"coal","CO2","permitted")
    coal.prepermit <- createStream(capacity.data.coal,"coal","CO2","pre-permit")
    coal.announced <-  createStream(capacity.data.coal,"coal","CO2","announced")
    coal.construction <-  createStream(capacity.data.coal,"coal","CO2","construction")
    coal.permitted.MW <- createStream(capacity.data.coal,"coal","MW","permitted")
    coal.prepermit.MW <- createStream(capacity.data.coal,"coal","MW","pre-permit")
    coal.announced.MW <-  createStream(capacity.data.coal,"coal","MW","announced")
    coal.construction.MW <-  createStream(capacity.data.coal,"coal","MW","construction")
    
    coal <- merge(coal.permitted,coal.prepermit,by="country",all=T)
    coal <- merge(coal,coal.announced,by="country",all=T)
    coal <- merge(coal,coal.construction,by="country",all=T)
    coal.MW <- merge(coal.permitted.MW,coal.prepermit.MW,by="country",all=T)
    coal.MW <- merge(coal.MW,coal.announced.MW,by="country",all=T)
    coal.MW <- merge(coal.MW,coal.construction.MW,by="country",all=T)

    coal.operating <- createStream(capacity.data.coal,"coal","CO2","operating",1937:2100)
    coal.operating.MW <- createStream(capacity.data.coal.MW,"coal","MW","operating",1937:2100)
    coal.committed <- coal.operating[,c(1,86:ncol(coal.operating))]
    
    # create steel data, but only the considered data. The comitted data is 
    steel.proposed <- createStream(capacity.data.steel,"steel","cap","proposed")
    steel.construction <- createStream(capacity.data.steel,"steel","cap","construction")
    steel.consid <- merge(steel.proposed,steel.construction,by="country",all=T)

    electricity.committed <- merge(coal.committed,gas.committed,all=T,by="country")
    
    names(electricity.committed)  <- gsub(".operating.",".committed.",names(electricity.committed),fixed=T)

#     otherindustry.proposed <- steel.proposed
#     names(otherindustry.proposed) <- gsub("steel","otherindustry",names(otherindustry.proposed),fixed=T)

    ## Implementing alternative assumption about "other industry" production (Steel about 40% of industrial emissions):
    otherindustry.proposed[,2:ncol(otherindustry.proposed)] <- 1.5 * otherindustry.proposed[,2:ncol(otherindustry.proposed)]

    # Writing all of the newly made considered and committed datasets to CSVs
    write.csv(electricity.committed,"data/electricity.committed.csv")
    write.csv(coal,"data/coal-considered.csv")
    write.csv(gas.consid,"data/gas-considered.csv")
    write.csv(steel.proposed,"data/steel-considered.csv")
    write.csv(otherindustry.proposed,"data/otherindustry-considered.csv")

    return(list(electricity.committed, coal, gas.consid, steel.consid, otherindustry.proposed))}
