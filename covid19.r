library(rvest)
library(tidyverse)
library(reshape2)
library(ggplot2)
library(plotly)
library(viridis)
library(curl)
library(emayili)
library(orca)
library(telegram.bot)

g_username <- 'youremail@domain.com'
g_password <- 'password'
g_port <- 587
g_host <- 'smtp.gmail.com'
to_email <- 'toxxxxx@domain.com'
bot_token <- 'xxxxxxxxxxxxx:xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxx'
bot_chat_id <- 'xxxxxxxxxxxxxx'


# GET DATA FROM WORDOMETER
getData <- function(){
  options(stringsAsFactors = FALSE)
  
  url_base <- "https://www.worldometers.info/coronavirus/"
  corona <- data.frame(
    "Country" = character(0),
    "Total_Cases" = character(0),
    "New_Cases" = character(0),
    "Total_Deaths" = integer(0),
    "New_Deaths" = character(0),
    "Total_Recovered" = character(0),
    "Active_Cases" = character(0),
    "Serious_Critical" = character(0),
    "Tot_Cases_1M_pop" = character(0))
  
  
  url <- paste0(url_base)
  pageTable <- url %>%
    read_html() %>%
    html_nodes(xpath='//*[@id="main_table_countries"]') %>%
    html_table()
  names(pageTable[[1]]) <- names(corona)
  corona <- rbind(corona, pageTable[[1]])
  
  # Remove comma characters in the columns
  corona$Total_Cases <- as.numeric(gsub(',','',corona$Total_Cases))
  corona$Total_Recovered <- as.numeric(gsub(',','',corona$Total_Recovered))
  corona$Total_Deaths <- as.numeric(gsub(',','',corona$Total_Deaths))
  corona$New_Cases <- as.numeric(gsub(',+','',corona$New_Cases))
  corona$Active_Cases <- as.numeric(gsub(',+','',corona$Active_Cases))
  corona$Serious_Critical <- as.numeric(gsub(',+','',corona$Serious_Critical))
  plotChart(corona)
  sendEmail(corona)
  sendTelegramBot(corona)
  delFiles()
  
  
}
  
# PLOT GRAPHS
plotChart <- function(corona){
  # plot the first 10 countries with the highest number of cases
  plot10 <- head(corona,10)
  plotMelt<-plot10 %>% select(Country,Total_Cases,Total_Recovered,Total_Deaths,Serious_Critical) %>% melt(id.vars="Country")
  plotNotMelt<-plot10 %>% select(Country,Total_Cases,Total_Recovered,Total_Deaths,Serious_Critical)
  
  
  p <- ggplot(plotMelt, aes(fill=variable, y=value, x=Country)) +
    geom_bar(position="dodge", stat="identity") +
    scale_fill_viridis(discrete = T) +
    ggtitle("CORONA VIRUS") +
    theme_minimal() +
    xlab("")
  p
  # fig <- plot_ly(plotNotMelt, x = ~Country, y = ~Total_Cases, type = 'bar', name = 'Total Cases')
  # fig <- fig %>% add_trace(y = ~Total_Recovered, name = 'Total Recovered')
  # fig <- fig %>% add_trace(y = ~Total_Deaths, name = 'Total Deaths')
  # fig <- fig %>% add_trace(y = ~Serious_Critical, name = 'Serious Critical')
  # fig <- fig %>% layout(yaxis = list(title = 'Number Of Cases'), barmode = 'group',title ="CORONA PANDEMIC")
  # fig
  
  write.csv(corona, 'coronaV.csv')
  ggsave(plot = p,"coronaV.png",scale = 1)
  
}
  
  
  # SENDING EMAIL FUNCTION
  sendEmail <- function(corona){
    
    msg <- paste0(
      "<h2>Hello Mary</h2> <br>",
      "<b style=color:red>Total Cases:&nbsp;",last(corona$Total_Cases),"</b> <br>",
      "<b style=color:red >Total Deaths:&nbsp;",last(corona$Total_Deaths),"</b> <br>",
      "<b style=color:purple>Recovered Cases:&nbsp;",last(corona$Total_Recovered),"</b> <br>",
      "<b style =color:red>Critical Serious:&nbsp;",last(corona$Serious_Critical),"</b> <br>"
    )
    
    email <- envelope() %>%
      from(g_username) %>%
      to(to_email) %>%
      subject("ℍ𝔼ℝ𝔼 𝕀𝕊 𝕋𝕆𝔻𝔸𝕐𝕊 ℂ𝕆ℝ𝕆ℕ𝔸 𝕍𝕀ℝ𝕌𝕊 𝕌ℙ𝔻𝔸𝕋𝔼 [ ℂ𝕆𝕍𝕀𝔻𝟙𝟡] 👹") %>% 
      html(msg) %>% 
      attachment("coronaV.png") %>% 
      attachment("coronaV.csv")
    
    smtp <- server(host = g_host,
                   port = g_port,
                   username = g_username,
                   password = g_password)
    
    smtp(email, verbose = TRUE)
    
  }
  
  
  sendTelegramBot <- function(corona){
    bot = Bot(token = bot_token)
    msg <- paste0("Hello John",
                  " ℍ𝔼ℝ𝔼 𝕀𝕊 𝕋𝕆𝔻𝔸𝕐𝕊 ℂ𝕆ℝ𝕆ℕ𝔸 𝕍𝕀ℝ𝕌𝕊 𝕌ℙ𝔻𝔸𝕋𝔼 [ ℂ𝕆𝕍𝕀𝔻𝟙𝟡] 👹 ",
                  "Total Cases:",last(corona$Total_Cases),

                  "Total Deaths:",last(corona$Total_Deaths),

                  "Recovered Cases:",last(corona$Total_Recovered),
                  "Critical Serious:",last(corona$Serious_Critical)
    )

    bot$sendMessage(chat_id = bot_chat_id, text = msg)
    bot$sendPhoto(chat_id = bot_chat_id, photo = 'coronaV.png')
    bot$sendDocument(chat_id = bot_chat_id, document = 'coronaV.csv')


  }
  
  
  # DELETE FILES GENERATED FOR NEXT NOTIFICATION
  delFiles <- function(){
    fn <- c('coronaV.png','coronaV.csv')
    for (n in fn){
      if (file.exists(n)) 
      file.remove(n)
    }
    print("FILES DELETED !!!")
  }
  
  
  
  getData()
  
  

  #   # usr/bin/Rscript --vanilla coronavirus.R                                     
  
  
 
