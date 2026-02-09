# GEO 371T - Climate Data

## 1. Connecting to the TACC Analysis Portal

The TACC Analysis Portal (TAP) provides a web-interface for starting Jupyter Notebook servers on high-performance compute nodes. [You can view more detailed documentation here](https://docs.tacc.utexas.edu/tutorials/TAP/) or just follow the steps below. Start by logging into web-app:

[https://tap.tacc.utexas.edu/](https://tap.tacc.utexas.edu/)

Once logged in, you should see a menu that looks like this:

![Starting page when you connect to TAP](./assets/TAP_start_page.png)

For GEO 371T, we have an allocation on Lonestar6 ([you can read more about LS6 here](https://tacc.utexas.edu/systems/lonestar6/)) and a reservation for quickly getting through the queue during lecture. The reservation name may occasionally change, but the class allocation name will remain the same. Select the entries from drop down menus shown below:

```
Submit New Job
--------------

System: Lonestar6
Application: Jupyter Notebook
Queue: normal
    (can also use "development" if reservation isn't available)
Node: 1
Tasks 1 
    (take note, we may increase this later for handling bigger datasets)


Optional Arguments
------------------

Time Limit: You can change the 2-hour default (max. 2 hrs for "development" queue)
Reservation: Ask Dr. Persad, can help get through queue wait times
```

![Menu selections to start notebook server](./assets/TAP_menus.png)

Then hit the "Submit" button to put your request for a Jupyter Notebook server in the queue on LS6.

![Submit button to send job to LS6](./assets/TAP_submit_job.png)

The web-app should then automatically redirect you to a "TAP Job Status" page that actively monitors your server. It may wait in the queue for a bit, but eventually it should appear as "RUNNING" and prompt you to connect.

![Connect to your Jupyter Notebook server](./assets/TAP_connect.png)

Connecting to the server will redirect you to its Jupyter Notebook interface, which is actively being hosted on a compute node apart of LS6. Keep in mind that the server will only remain online for 2 hours by default (this can be changed on the job menu before submitting). 

### **After 2 hours, the server will shutdown and all unsaved work will be lost.**

**Make sure to frequently save your work and pay attention to the time!**

If you get disconnected from your server, you can reconnect by revisiting the [TAP homepage](https://tap.tacc.utexas.edu/):

![Reconnecting to your Jupyter Notebook server from the TAP homepage](./assets/TAP_reconnect.png)


## 2. Downloading and Updating the Class Repostiory

Once connected to LS6, you will need to clone this repository to gain access to the class materials. You can do this from a Jupyter Notebook server or [via SSH](https://docs.tacc.utexas.edu/hpc/lonestar6/#access) if you prefer that. For the Notebook approach, start a terminal by clicking on the "New" drop-down menu in the top right corner and then "Terminal":

![Starting a terminal in the Jupyter Notebook server](./assets/TAP_terminal.png)

First navigate to your home directory:

```
cd $HOME
```

Then use `git` to clone this repository:

```
git clone https://github.com/PersadAeroClimateLab/GEO371T-Climate-Data.git
```

Return to your Jupyter interface, the `GEO371T-Climate-Data/` directory should be visible:

![Repo directory should be in Jupyter Notebook](./assets/TAP_git.png)

This class is still being actively developed, so we will periodically push updates to the main branch of this GitHub repository. However, the copy of this repository in your home directory does not automatically update and will require manual intervention. Luckily, `git` makes this easy. In a terminal, run the following commands to update:

```
cd $HOME/GEO371T-Climate-Data
git pull
```