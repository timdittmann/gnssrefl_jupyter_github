# Method

To summarize, direct (blue) and reflected (red) GNSS signals interfere and create
an interference pattern that can be observed in GNSS Signal to Noise Ratio (SNR) data as a satellite rises or sets. 
The frequency of this interference pattern is directly related to the height of the GNSS antenna phase
center above the reflecting surface, or reflector height RH (purple). *The primary goal of this software 
is to measure RH.* This parameter is directly related to changes in snow height and water levels below
a GNSS antenna. This is why GNSS-IR can be used as a snow sensor and tide gauge. GNSS-IR can also be 
used to measure soil moisture, but the code to estimate soil moisture is not as strongly related to RH as
snow and water. We will be posting the code you need to measure soil moisture later in the year.

<p align=center>
<img src="https://gnss-reflections.org/static/images/overview.png" width="500" />
</p>

This code is meant to be used with Signal to Noise Ratio (SNR) data. This is a SNR sample for a site in the 
the northern hemisphere (Colorado) and a single GPS satellite. The SNR data are plotted with respect to time - however,
we have also highlighted in red the data where elevation angles are less than 25 degrees. These are the data used in 
GNSS Interferomertric Reflectometry GNSS-IR. You can also see that there is an overall smooth polynomial signature
in the SNR data. This represents the dual effects of the satellite power transmission level and the antenna 
gain pattern. We aren't interested in that so we will be removing it with a low order polynomial (and 
we will convert to linear units on y-axis). 

<p align=center>
<img src="https://github.com/kristinemlarson/gnssrefl/blob/master/docs/p041-snr.png" width="600"/>
</p>

After that polynomial is removed, we will concentrate on the *rising* 
and *setting* satellite arcs. That is the red parts on the left and right.  
Here you can see those next two steps. On the top is the "straightened" SNR data. Instead of time,
it is plotted with respect to sine of the elevation angle. It was shown a long time ago by Penina 
Axelrad that the frequency extracted from these data is representative of the reflector height.
Here a periodogram was used to extract this frequency, and that is shown below, with the x-axis 
units changed to reflector height. In a nutshell, that is what this code does. It figures out the 
rising and setting satellite arcs in all the azimuth regions you have said are acceptable. It does a 
simple analysis (removes the polynomial, changes units) and uses a periodogram to look at the 
frequency content of the data. You only want to report RH when you think the peak on the periodogram is 
significant. There are many ways to do this - we only use two quality control metrics:

* is the peak larger than a user-defined value  (amplitude of the dominant peak in your periodogram)

* is the peak divided by a "noise" metric larger than a user-defined value. The code calls this the peak2noise.

<p align=center>
<img src="https://github.com/kristinemlarson/gnssrefl/blob/master/tests/for_the_web.png" width="600"/>
</p>

The Colorado SNR example is for a fairly planar field where the RH for the rising and setting arc 
should be very close to the same name. What does the SNR data look like for a more extreme case? 
Shown below is the SNR data for [Peterson Bay](https://gnss-reflections.org/static/images/PBAY.jpg), where the rising arc (at low tide) has a very different
frequency than during the setting arc (high tide). This gives you an idea of how the code can be 
used to measure tides. 

<p align=center>
<img src="https://github.com/kristinemlarson/gnssrefl/blob/master/docs/pbay-snr.png" width="600"/>
</p>

A couple common sense issues: one is that since you define the noise region, if you make it really large, that 
will artificially make the peak2noise ratio larger. I have generally used a region of 6-8 meters for this 
calculation. So in the figure above the region was for 0-6 meters. The amplitude can be tricky because 
some receivers report low SNR values, which then leads to lower amplitudes. The default amplitude values are 
for the most commonly used signals in GNSS-IR (L1, L2C, L5, Glonass, Galileo, Beidou). The L2P data
used by geodesists are generally not useable for reasons to be discussed later.

Even though we analyze the data as a function of sine of elevation angle, each satellite arc
is associated with a specific time period. The code keeps track of that and reports it in the final answers.
It also keeps track of the average azimuth for each rising and setting satellite arc that passes quality 
control tests.

What do these satellite reflection zones look like? Below are 
photographs and [reflection zone maps](https://gnss-reflections.org/rzones) for two standard GNSS-IR sites, 
one in the northern hemisphere and one in the southern hemisphere.

<p align=center>
<table align=center>
<TR>
<TH>Mitchell, Queensland, Australia</TH>
<TH>Portales, New Mexico, USA</TH>
</TR>
<TR>
<TD><img src=http://gnss-reflections.org/static/images/MCHL.jpg width=300></TD>

<TD><img src=http://gnss-reflections.org/static/images/P038.jpg width=300></TD>
</TR>
<TR>
<TD><img src=https://github.com/kristinemlarson/gnssrefl/blob/master/tests/use_cases/mchl_google.jpg width=300></TD>
<TD><img src=https://github.com/kristinemlarson/gnssrefl/blob/master/tests/use_cases/p038_google.jpg width=300></TD>
</TR>
</table>
</p>
Each one of the yellow/blue/red/green/cyan clusters represents the reflection zone
for a single rising or setting GPS satellite arc. The colors represent different elevation angles - 
so yellow is lowest (5 degrees), blue (10 degrees) and so on. The missing satellite signals in the north
(for Portales New Mexico) and south (for Mitchell, Australia) are the result of the GPS satellite 
inclination angle and the station latitudes. The length of the ellipses depends on the height of the 
antenna above the surface - so a height of 2 meters gives an ellipse that is smaller than one 
that is 10 meters. In this case we used 2 meters for both sites - and these are pretty 
simple GNSS-IR sites. The surfaces below the GPS antennas are fairly smooth soil and that 
will generate coherent reflections. In general, you can use all azimuths at these sites.  
<P>
<P>
Now let's look at a more complex case, station <code>ross</code> on Lake Superior. Here the goal 
is to measure water level. The map image (panel A) makes it clear
that unlike Mitchell and Portales, we cannot use all azimuths to measure the lake. To understand our reflection 
zones, we need to know the approximate lake level. That is a bit tricky to know, but the 
photograph (panel B) suggests it is more than the 2 meters we used at Portales - 
but not too tall. We will try 4 meters and then check later to make sure that was a good assumption.  
</P>

<p align=center>
<table align=center>
<TR>
<TD>A. <img src=https://github.com/kristinemlarson/gnssrefl/blob/master/tests/use_cases/ross-google.jpg width=300> <BR>
Map view of station ROSS </TD>
<TD>B. <img src=https://gnss-reflections.org/static/images/ROSS.jpg width=300> <BR>
Photograph of station ROSS</TD>
</TD>
</TR>
<Tr>
<TD>C. <img src=https://github.com/kristinemlarson/gnssrefl/blob/master/tests/use_cases/ross-first.jpg width=300><BR>
Reflection zones for GPS satellites at elevation <BR>angles of 5-25 degrees 
for a reflector height of <BR>4 meters.</TD> 
<TD>D. <img src=https://github.com/kristinemlarson/gnssrefl/blob/master/tests/use_cases/ross-second.jpg width=300><BR>
Reflection zones for GPS satellites at elevation <BR>angles of 5-15 degrees 
for a reflector height of <BR>4 meters.  </TD>
</Tr>
</table>
</p>

Again using the reflection zone web app, we can plot up the appropriate reflection zones for various options.
Since <code>ross</code> has been around a long time, [http://gnss-reflections.org](https://gnss-reflections.org) has its coordinates in a 
database. You can just plug in <code>ross</code> for the station name and leave 
latitude/longitude/height blank. You *do* need to plug in a RH of 4 since mean 
sea level would not be an appropriate reflector height value for this 
case. Start out with an azimuth range of 90 to 180 degrees.
Using 5-25 degree elevation angles (panel C) looks like it won't quite work - and going all the way to 180 degrees
in azimuth also looks it will be problematic. Panel D shows a smaller elevation angle range (5-15) and cuts 
off azimuths at 160. These choices appear to be better than those from Panel C.  
It is also worth noting that the GPS antenna has been attached to a pier - 
and *boats dock at piers*. You might very well see outliers at this site when a boat is docked at the pier.

Once you have the code set up, it is important that you check the quality of data. This will also 
allow you to check on your assumptions, such as the appropriate azimuth and elevation angle 
mask and reflector height range. This is one of the reasons <code>quickLook</code> was developed. 
