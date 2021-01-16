# time-manager

----------------------------

force close network by time algh.  
CLI and GUI  (will add web UI)  
plot date-time 2d in terminal UNICODE or pyqtgraph GUI.  
sklearn cluster and show name in pyqtgraph plot  
auto collect data from linux wtmp, chrome and firefox browser. (will add more)
show current running tasks on terminal  

## improve
browser collector auto filter already records(part finally)  
cache cluster result to database, use less cpu.  
auto run collect in system crontab  
add once run collector to 'collectors' table  
split sqlite TABLE 'task' to 'plans' and 'real_record'  
filter tasks  
notify to gnome-shell  
food expiration date  
things place and WMS system  
multi-client sync  
add web UI  
chrome and firefox plugin  
auto classify things use NLP  

----------------------------

## Data Flow Diagram
```
      +---------- raw data -------[filter]----------+
      |                                             v
+------------+         ./``````````\.        +--------------
| collector  |       ./`  analyzer  `\.      |   recorder
|            | --->  |   threshold    | ---> |
|brow cam mic|       `\.   NLP CV   ./`      | sqlite ffmpeg
+------------+         `\.________./`        +--------------
                          |            ._%          ^
                 warnings |         ._/ commit      |
                          v      _./                v
                     +-------------+         +-------------+
                     |   notify    |         |     UI      |
                     | sound gnome |         |             |
                     | email commd |         | CLI GUI Web |
                     +-------------+         +-------------+
```

### collects
| name       | stat | desc                  |
| :--------- | :---:| :-------------------- |
| chrome     |  OK  | visit time            |
| firefox    |  OK  | visit time            |
| linux wtmp |  OK  | boot and shutdown     |
| git        |  no  | git commit time       |
| IDE        |  no  |                       |
| walk step  |  no  | Android phone         |
| x(t) signal|  no  | any physical quantity |

### analyzer
| name         | input | output| stat | desc                  |
| :----------- | :---: | :---: | :---:| :-------------------- |
| eyes screen  | image |       |  OK  | MTCNN Face detection  |
| screen time  | event |       |  no  |
| web time     | event |       |  no  |
| web NLP      | text  |       |  no  |
| web image    | image |       |  no  |

### recoder
| name        | dtype | desc             |
| :---------- | :---: | :--------------- |
| sqlite      | hybrid|
| ffmpeg      | video |
| auto sync   |

### notify
sound, gnome-shell, other device, email, run command.  

| name        | time-level | stat | desc        |
| :---------- | ---------: | :---:| :---------- |
| sound       |     1s-15s |  OK  |
| gnome-shell |   5s-10min |  no  |
| other device|      >5min |  no  |
| email       |      >1day |  no  |
| run command |          0 |  no  |
| commit      |            |      | after notify, you can commit.

### UI
| name         |   CLI   |    GUI    |  Web(NotImp) | desc           |
| :----------- | :-----: | :-------: | :----------: | :------------- |
| date-time 2d | unicode | pyqtgraph |              | image per year |
| custom plot  |         | plt, pg   |              | simple use     |
