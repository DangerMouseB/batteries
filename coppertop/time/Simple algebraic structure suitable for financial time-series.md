
### Problem we're trying to solve

I've used systems where the following mistakes cause problems:

#### 1) treating abstract time as observed time 

For example, combine a csv emailed from New York with a csv dumped in London - the 
location context of the timestamps is usually abstracted from the csv format. Save 
that to disk and load later (e.g. at quarter's end) and you have a recipe for errors 
and mis-spent time.

#### 2) accidentally looking into the future
Especially when sorting data with different precision time, e.g. minute samples with 
hourly of daily samples. Sometimes bars are labelled and sorted with the 
opening timestamp.

#### 3) trying to build a unified view with data from different times
For example yield curves that use the *close* but the exact time of that *close* has 
not been consistenly determined for all instruments involved.

<br> 


### Solution

This is a simple model / algebraic structure [^1] for accurately and specifically 
representing time that is intended to be easy to use yet discourages the above errors.

#### Types
ObservedDateTime - datetime.datetime with a pytz.timezone\
ObservedTimeOfDay - datetime.time plus a pytz.timezone\
AbstractDateTime - datetime.datetime\
AbstractTimeOfDay - datetime.time\
AbstractDate - datetime.date\
ObserversContext - e.g. pytz.timezone

The word Abstract is used to serve as a mild warning about conflating the computer 
type with the richer human experience that often goes under a similar name.

Conceptually `UTC` is a subtype of ObservedDateTime, `4:15pm London` is a subtype 
of ObservedTimeOfDay and `9am` is a subtype of AbstractTimeOfDay.

#### Enums
* precision {h, m, s, ms, us, hns}
* observers context
  * UTC
  * IanaCity
  * IanaTz
  * FpMLCity
  
  
#### Structural (creation and conversion) operations
parseXXX where XXX is the Type, e.g. parseAbstractDate\
toString("<format>")\
toCtx(ctx) - to convert between contexts\
asObserved(ctx) - coerce to an observers context to AbstractDatTime and AbstractTime\
asOf(precision) - round up to precision to make times comparable


#### Relevant algebraic operations
DaysTime {days, seconds, subsecond, precision}\
UTC addPeriod(UTC, aDayTime)\
DaysTime periodDiff(UTC1, UTC2)


#### Example domain specific Algebraic operations - defined elsewhere
YearMonth\
MonthDay\
addPeriod, periodDiff - derivatives rules\
addPeriod, periodDiff - cycle rules

Calendars and working hours might be needed to perform addPeriod.

----

[^1]: see https://en.wikipedia.org/wiki/Algebraic_structure




