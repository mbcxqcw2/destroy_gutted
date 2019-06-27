import sys
import numpy as np

#########################################################################################
#INPUT PARAMETERS

a=sys.argv

n_inputs=2

if len(a)!=n_inputs+1:
    print "Error: {0} arguments required. {1} provided.".format(n_inputs,len(a))

# Input DESTROY candidate file to cluster
InFile = str(a[1])
print 'DESTROY Candidate file to cluster: {0}'.format(InFile)

# Output clustered candidate file name

OutFile=str(a[2])

print 'Clustered output file name: {0}'.format(OutFile)


#########################################################################################
#FUNCTION

def ClusterDestroy(DestroyFile,OutFile):
    """
    Clusters destroy candidates. Sorts candidates based on start time, and finds those
    which overlap. Gets highest S/N candidate only from each cluster group and writes to new file.
    Algorithm adopted from:
    
    https://stackoverflow.com/questions/14885188/checking-for-overlap-between-time-spans
    https://stackoverflow.com/questions/2244964/finding-number-of-overlaps-in-a-list-of-time-ranges
    
    INPUTS :
    
    DestroyFile : (str) path and filename of destroy output candidate file
    OutFile     : (str) path and filename of output clustered candidate file
    
    OUTPUTS :
    
    Stores a new, smaller file based on original input DestroyFile.
    
    """
    
    #initialise destroy candidate array (contains four columns)
    cands=np.empty((1,4))
    #load file
    check=np.loadtxt(DestroyFile)
    if check.shape!=(0,): #if cand file is not empty
        if check.shape==(4,): #if only one candidate, reshape to allow appending
            check=check.reshape(1,4)
        cands=np.concatenate((cands,check),axis=0) #append candidates
    elif check.shape==(0,):#if cand file is empty
        print('WARNING: INPUT CANDIDATE FILE IS EMPTY') #print warning
        return #exit
    #reassign candidates to arrays
    dms = cands[:,0]
    downsamp = cands[:,1] #known as nsmoothings in destroy files. check this is boxcar width in bins.
    sample = cands[:,2]
    snrs = cands[:,3]

    #get sample extent of each cand
    startsamps = sample - (downsamp/2)
    endsamps = sample + (downsamp/2)
    
    #get all candidate time intervals in candidate list
    allcandlist = zip(startsamps,endsamps,sample,downsamp,snrs,dms)
    #sort list by start times
    allcandlist_sorted = sorted(allcandlist, key=lambda x: x[0])

    #initialise  array to hold potentially related cands (include a placeholder candidate)
    #newcand = True
    relcands = [np.zeros(6)]

    #initialise array to hold only the peak SNR candidates from clustered cands
    peakcands = []

    #loop over all candidates
    for x in range(1,len(allcandlist_sorted)):
        #newcand = False
    
        #if two sequential candidates overlap, store them in the related cands array
        if allcandlist_sorted[x-1][1] > allcandlist_sorted[x][0]:
            #print "{0} overlaps with {1}".format( allcandlist_sorted[x-1], allcandlist_sorted[x] )
            relcands.append(allcandlist_sorted[x-1])
            relcands.append(allcandlist_sorted[x])
        
        #if the two sequential candidates don't overlap, you have reached the end of the clustered candidate.
        else:
            #Find the cand in the cluster with the largest SNR
            peakcand = sorted(relcands,reverse=True,key=lambda x: x[4])[0]
            #Append it to the peak SNR cands array
            peakcands.append(peakcand)
            #start a new clustered cand, reset the related cands array
            #print 'newcand'
            #newcand = True
            relcands=[np.zeros(6)]
            relcands.append(allcandlist_sorted[x])

    
    peakcands=np.array(peakcands,dtype='str')
    
    #extract relevant factors to store to new candidate file
    peakdms = peakcands[:,5]
    peakdownsamp = peakcands[:,3]
    peaksample = peakcands[:,2]
    peaksnr = peakcands[:,4]
    
    #save clustered candidates to new file
    np.savetxt(OutFile,np.c_[peakdms,peakdownsamp,peaksample,peaksnr],fmt='%s')
    
    return 
        

        
#########################################################################################
#BEGIN  FUNCTION

ClusterDestroy(InFile,OutFile)
