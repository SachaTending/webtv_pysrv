var gEmbedTag;
var gNumCategories = 0; // how many categories does the user like?
var gCurrentIndex; // index of current teaser
var gNextIndex; // index of next teaser for preloading
var gNextNextIndex; // index of subsequent teaser for preparing to preload. Really.
var gEmbedURL; // prefix of URL to point embed to (minus category name)
var gLinkURL; // prefix of URL that embed should link to (minus category name)
var gCategories = new Array(); // Names of info categories
var gTeaserBlacklisted = new Array(); // 1 iff we've tried to load this teaser and timed out
var gTimeoutHandle; // handle to timer for timeout so we can cancel it if we succeed
var gRotateTimerHandle = nil; // handle to timer for rotation so we can cancel it when going to generic teaser
var gStale; // 1 iff we've reverted to generic teaser
var gWeather = new Array(); // array of weather predictions to rotate through
var gWeatherIndex; // index of which weather prediction we're showing
var gFirstWeatherIndex; // index of first slot in weather rotation
var gWeatherTimeout;
var gNumLoaded = 0; // 1 for home page, 1 for loading teaser; 2 required to start rotation
var gRemainderOfScriptLoaded = false;

function Initialize() {
    ++gNumLoaded;
    if (gNumLoaded < 2)
        return;
    var i;
    gEmbedURL = "wtv-center:/custom-info-teaser?quotesPerTeaser=5&template=GrungeTeasers.tmpl&info=";
    gLinkURL = "wtv-center:/custom-info-page#";
    if ("WebTVToday" != "") {
        gCategories[0] = "WebTVToday";
        gNumCategories += 1;
    }
    if ("News" != "") {
        gCategories[1] = "News";
        gNumCategories += 1;
    }
    if ("Weather" != "") {
        gCategories[2] = "Weather";
        gNumCategories += 1;
    }
    if ("Shopping" != "") {
        gCategories[3] = "Shopping";
        gNumCategories += 1;
    }
    if ("Entertainment" != "") {
        gCategories[4] = "Entertainment";
        gNumCategories += 1;
    }
    if ("Sports" != "") {
        gCategories[5] = "Sports";
        gNumCategories += 1;
    }
    if ("Stocks" != "") {
        gCategories[6] = "Stocks";
        gNumCategories += 1;
    }
    if ("Intro" != "") {
        gCategories[7] = "Intro";
        gNumCategories += 1;
    }
    for (i = 0; i < gNumCategories; ++i) {
        gTeaserBlacklisted[i] = 0;
    }
    gCurrentIndex = 0;
    gNextIndex = 0;
    gStale = 0;
    gEmbedTag = document.customInfoEmbed;
    gLinkTag = document.customInfoLink;
    if (typeof gEmbedTag.document == "undefined") {
        setTimeout(Initialize, 100); // wait 0.1 seconds and try again
        return;
    }
    if (gRemainderOfScriptLoaded != "true") {
        setTimeout(Initialize, 100); // wait 0.1 seconds and try again
        return;
    }
    if (typeof gRotateTimerHandler != "undefined" && gRotateTimerHandler != null) {
        return;
    }
    gRotateTimerHandle = setTimeout(RotateToNextTeaser, 6000);
    setTimeout(CheckConnectionStatus, 600000);
}

function CheckConnectionStatus() {
    var nextPoll;
    // Did we just reconnect?
    if (navigator.networkOnline() && gStale == 1) {
        ResumeRotation();
        nextPoll = 600000;
    }
    // Are we disconnected?
    else if (!navigator.networkOnline()) { // Did we just disconnect recently?
        if (gStale == 0)
            RevertToGenericTeaser();
        nextPoll = 1000;
    }
    // We're still connected...
    else {
        nextPoll = 60000;
    }
    setTimeout(CheckConnectionStatus, nextPoll);
}

function RevertToGenericTeaser() {
    gStale = 1;
    gCurrentIndex = -1;
    clearTimeout(gTimeoutHandle);
    clearTimeout(gRotateTimerHandle);
    gEmbedTag.src = gEmbedURL + gCategories[0] + "&i1=" + gCategories[0] + "&i2=" + gCategories[1] + "&i3=" + gCategories[2] + "&i4=" + gCategories[3] + "&i5=" + gCategories[4] + "&i6=" + gCategories[5] + "&i7=" + gCategories[6] + "&i8=" + gCategories[7];
    if (typeof gEmbedTag.document == "undefined") {
        WriteEvergreenTeaser();
    }
}

function WriteEvergreenTeaser() {
    gEmbedTag.document.open();
    gEmbedTag.document.write("<html><head><display showwhencomplete></head> " +
        "<body background=wtv-content:/ROMCache/BackgroundWebTVToday_a.swf BGCOLOR=#949484>" +
        "<table cellspacing=0 cellpadding=0 width=373 height=193>" +
        "<tr><td valign=middle align=center>" +
        "<table cellspacing=0 cellpadding=0>" +
        "<tr height=44><td width=100><SPACER TYPE=BLOCK WIDTH=100 HEIGHT=44>" +
        "<tr height=40><td width=100><SPACER TYPE=BLOCK WIDTH=100 HEIGHT=40><td width=267><SPACER TYPE=BLOCK WIDTH=267 HEIGHT=40><td width=6>" +
        "<tr height=60><td width=100><SPACER TYPE=BLOCK WIDTH=100 HEIGHT=60><td maxlines=2 valign=top align=left width=267><font size=+2><B>Get the latest in</B></font><br><font size=+2><b>WebTV Today</b></font><td width=6>" +
        "<tr height=49><td width=100><SPACER TYPE=BLOCK WIDTH=100 HEIGHT=49><td width=267 valign=middle align=right><td width=6>" +
        "</table></table>" +
        "</body></html>");
    gEmbedTag.document.close();
    gLinkTag.href = "wtv-center:/center?info=WebTVToday";
}

function ResumeRotation() {
    gStale = 0;
    RotateToNextTeaser();
}

function FindNext(startHere) {
    var nextIndex = startHere + 1;
    nextIndex = nextIndex % gNumCategories;
    // If the next teaser is blacklisted, go to the following one
    if (gTeaserBlacklisted[nextIndex] == 1) {
        ++nextIndex;
        nextIndex = nextIndex % gNumCategories;
    }
    while (gCategories[nextIndex] == null) {
        ++nextIndex;
        nextIndex = nextIndex % gNumCategories;
    }
    return nextIndex;
}

function RotateToNextTeaser() {
    if (gStale == 0) {
        gCurrentIndex = FindNext(gCurrentIndex);
        // Point the embed to the proper URL
        if (gNumCategories > 1) {
            gTimeoutHandle = setTimeout(Timeout, 40000);
        }
        if (gCategories[gCurrentIndex] == "Intro") {
            CustomEmbedLoaded();
        } else {
            gEmbedTag.src = gEmbedURL + gCategories[gCurrentIndex] + "&i1=" + gCategories[0] + "&i2=" + gCategories[1] + "&i3=" + gCategories[2] + "&i4=" + gCategories[3] + "&i5=" + gCategories[4] + "&i6=" + gCategories[5] + "&i7=" + gCategories[6] + "&i8=" + gCategories[7];
            if (gCategories[gCurrentIndex] == "Sports") {
                gLinkTag.href = "wtv-center:/center?info=Sports";
            } else if (gCategories[gCurrentIndex] == "SportsNews") {
                gLinkTag.href = "wtv-center:/center?info=Sports";
            } else if (gCategories[gCurrentIndex] == "Entertainment") {
                gLinkTag.href = "wtv-center:/center?info=Entertainment";
            } else if (gCategories[gCurrentIndex] == "News") {
                gLinkTag.href = "wtv-center:/center?info=News";
            } else if (gCategories[gCurrentIndex] == "Stocks") {
                gLinkTag.href = "wtv-center:/center?info=Money#quotes";
            } else if (gCategories[gCurrentIndex] == "Weather") {
                gLinkTag.href = "wtv-center:/center?info=News#weather";
            } else if (gCategories[gCurrentIndex] == "Shopping") {
                gLinkTag.href = "wtv-center:/center?info=Shopping";
            } else {
                gLinkTag.href = "wtv-center:/center?info=WebTVToday";
            }
        }
    }
}

function Timeout() {
    if (!navigator.networkOnline()) {
        RevertToGenericTeaser();
    } else {
        gTeaserBlacklisted[gCurrentIndex] = 1;
        SetRotateTimer();
    }
}

function SetRotateTimer() {
    var delay;
    if (gCategories[gCurrentIndex] == "Weather")
        delay = 8700;
    else
        delay = 7000;
    if (gNumCategories > 1) {
        gRotateTimerHandle = setTimeout(RotateToNextTeaser, delay);
    }
}

function CustomEmbedLoaded() {
    var doc;
    clearTimeout(gWeatherTimeout);
    doc = document.customInfoEmbed.document;
    if (gCategories[gCurrentIndex] == "Weather" && doc.weatherForm == nil) {
        setTimeout(CustomEmbedLoaded(), 100);
        return;
    }
    if (gStale == 0) {
        clearTimeout(gTimeoutHandle);
        SetRotateTimer();
    }
    if (gCategories[gCurrentIndex] == "Weather" && typeof doc.weatherForm == "object") {
        doc.weatherForm.disp1a.value = doc.weatherForm.disp1.value;
        doc.weatherForm.disp2a.value = doc.weatherForm.disp2.value;
        gFirstWeatherIndex = 0;
        gWeatherIndex = gFirstWeatherIndex;
        gWeatherTimeout = setTimeout(RotateWeather, 2900);
    }
}

function RotateWeather() {
    var doc;
    var str1;
    var str2;
    doc = document.customInfoEmbed.document;
    if ((gCategories[gCurrentIndex] == "Weather") &&
        (doc.weatherForm != nil) &&
        (typeof doc.weatherForm == "object")) {
        gWeatherIndex += 1;
        if (gWeatherIndex > 2) {
            gWeatherIndex = gFirstWeatherIndex;
        }
        if (gWeatherIndex == 1) {
            str1 = doc.weatherForm.disp1b.value;
            str2 = doc.weatherForm.disp2b.value;
        } else if (gWeatherIndex == 2) {
            str1 = doc.weatherForm.disp1c.value;
            str2 = doc.weatherForm.disp2c.value;
        } else {
            str1 = doc.weatherForm.disp1a.value;
            str2 = doc.weatherForm.disp2a.value;
        }
        doc.weatherForm.disp1.value = str1;
        doc.weatherForm.disp2.value = str2;
        if (gWeatherIndex != 2 || gNumCategories == 1) {
            gWeatherTimeout = setTimeout(RotateWeather, 2900);
        }
    }
}
gRemainderOfScriptLoaded = "true";