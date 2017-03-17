/*
** Copyright (C) 2008-2012 Erik de Castro Lopo <erikd@mega-nerd.com>
**
** All rights reserved.
**
** Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are
** met:
**
**     * Redistributions of source code must retain the above copyright
**       notice, this list of conditions and the following disclaimer.
**     * Redistributions in binary form must reproduce the above copyright
**       notice, this list of conditions and the following disclaimer in
**       the documentation and/or other materials provided with the
**       distribution.
**     * Neither the author nor the names of any contributors may be used
**       to endorse or promote products derived from this software without
**       specific prior written permission.
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
** "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
** TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
** PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
** CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
** EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
** PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
** OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
** WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
** OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
** ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

#include <sndfile.h>

#define	BLOCK_SIZE 512

static void
print_usage (char *progname)
{	printf ("\nUsage : %s <input file> <output file>\n", progname) ;
	puts ("\n"
		"    Where the output file will contain a line for each frame\n"
		"    and a column for each channel.\n"
		) ;

} /* print_usage */

static void
find_ticks (SNDFILE * infile, FILE * outfile, int channels, int sample_rate)
{
  float buf [channels * BLOCK_SIZE] ;
  int k, m, readcount;

  int sample_count = 0;
  double max[channels];
  int last_tick[channels];
  int first_tick[channels];
  int delta[channels];
  double thresh[channels];
  int tick_count[channels];

#define INHIBITION_PERIOD 480
  double sw_avg[INHIBITION_PERIOD];
  int sw_index=0;
  int i;
  double sum;
  double last_avg, last_time;

  double meas_offset;
  double cur_clock;
  
  
  memset( max, 0, sizeof(max) );
  memset( last_tick, 0, sizeof(last_tick) );
  memset( delta, 0, sizeof(delta) );
  memset( tick_count, 0, sizeof(tick_count) );
  memset( sw_avg, 0 , sizeof(sw_avg) );
  last_avg = 0.0;
  last_time = 0.0;
  
  /* TODO - add auto-thresh based on max amplitude seen */
  thresh[0]=0.5; /* ch 0 = left  = watch */
  thresh[1]=0.1; /* ch 1 = Right = PPS */
  //thresh[1]=0.5; /* ch 1 = Right = PPS */

#define REF_CHAN 1
#define MEAS_CHAN 0
	
  /* TODO - add live tracking of average sample rate */
  //double sample_rate_avg = 192004.318087;
  double sample_rate_avg = 192003.739919;
	
  /* TODO - add SWAVG over inhibition interval */
  /* TODO - add rate calc using SWAVG over inhibition interval */
	
	
  while ((readcount = sf_readf_float (infile, buf, BLOCK_SIZE)) > 0)
    {
      for (k = 0 ; k < readcount ; k++)
	{
	  sample_count++;

	  for (m = 0 ; m < channels ; m++)
	    {
	      /* track maximum amplitude */
	      if ( fabs(buf [k * channels + m])  > max[m]  )
		max[m] =  fabs(buf [k * channels + m]);

	      /* look for a reference pulse, or a watch tick */ 
	      if ( fabs(buf [k * channels + m])  > thresh[m]  )
		{
		  /* mark first tick */
		  if (  0 == first_tick[m] )
		    first_tick[m]=sample_count;

		  /* TODO - add variable no-trigger timing? */
		  /* REF = 100msec pulse, but AC coupling makes it appear as two pulses over 200msec */
		  if ( ((sample_count - last_tick[m]) > (sample_rate/4))  ||
		       ( 0 == last_tick[m] ))
		    {
		      tick_count[m]++;
		      delta[m] = sample_count - last_tick[m];

		      cur_clock = (double)sample_count / (double)sample_rate;
		      
		      if ( delta[m] > (3 * sample_rate / 2) )
			fprintf( stderr, "%09d %014.9f ch%d MISSED PULSE %09d\n",
				 sample_count, cur_clock, m+1, delta);

		      last_tick[m] = sample_count;
		      if ( MEAS_CHAN == m )
			{
			  printf ( "%09d %014.9f tic:%05d %6d (%11.9f) ref:%05d %6d (%11.9f) offs:% 6d (% 11.9f)\r",
				   sample_count, cur_clock, 
				   tick_count[MEAS_CHAN], delta[MEAS_CHAN], (double)delta[MEAS_CHAN] / (double)sample_rate,
				   tick_count[REF_CHAN],  delta[REF_CHAN],  (double)delta[REF_CHAN]  / (double)sample_rate,
				   sample_count - last_tick[REF_CHAN], (double)(sample_count - last_tick[REF_CHAN]) / (double)delta[REF_CHAN] );

			  meas_offset = (double)(sample_count - last_tick[REF_CHAN]) / sample_rate_avg;
			  
			  fprintf ( outfile, "OFF: %014.9f % 11.9f\n",
				    cur_clock, meas_offset );

			  /* store offset in sliding window average buffer */
			  sw_avg[sw_index++] = meas_offset;

			  /* calculate average over exact inhibition period */
			  if ( INHIBITION_PERIOD  == sw_index )
			    {
			      double new_avg;
			      double new_time;
			      
			      sw_index=0;
			      sum=0;
			      for ( i = 0; i<INHIBITION_PERIOD; i++)
				{
				  sum += sw_avg[i];
				}
			      new_avg = sum / (double)INHIBITION_PERIOD;
			      new_time = cur_clock;
			      
			      if ( last_time > 1.0 )
				printf("\n%09d %014.9f AVG:%11.9f s/d:% 6.3f s/y:% 6.2f\n",
				       sample_count, new_time, new_avg ,
				       (new_avg - last_avg) / (new_time - last_time ) * 86400.0,
				       (new_avg - last_avg) / (new_time - last_time ) * 86400.0 * 365.0 );
			      else
				printf("\n%09d %014.9f AVG:%11.9f\n",
				       sample_count, new_time, new_avg );
			      last_avg = new_avg;
			      last_time = new_time;
			    } /* END IF (end of an inhibition period) */
			} /* END IF (watch tick) */
		    } /* END IF (new pulse detected) */
		} /* END IF (above pulse threshold) */
	    } /* END FOR (all channels) */
	} /* END FOR (all samples in buffer) */
    } /* END WHILE (more buffers in file) */

  printf("\n");
  printf ( "max amplitude: %11.9f %11.9f\n",max[0],max[1]);
  printf ( "time resolution: %11.9f\n",1.0/(double)sample_rate);
  printf ( "tick count: %04d %04d\n",tick_count[0],tick_count[1]);
  printf ( "sample_rate_avg: %14.9f\n",sample_rate_avg);

  for ( m=0; m < channels; m++)
    if ( 1 == tick_count[m] )
      fprintf ( stderr, "ch: %d only 1 tick detected, cannot perform math\n",m);
    else 
      printf ( "ch: %d ticks:%05d first:%08d last:%08d avg: %8.6f (%11.9f)\n",
	       m, tick_count[m], first_tick[m], last_tick[m],
	       (last_tick[m] - first_tick[m]) / ((double)tick_count[m] - 1),
	       (last_tick[m] - first_tick[m]) / (((double)tick_count[m] - 1) * (double)(sample_rate)) );

  return ;
} 

int
main (int argc, char * argv [])
{	char 		*progname, *infilename, *outfilename ;
	SNDFILE		*infile = NULL ;
	FILE		*outfile = NULL ;
	SF_INFO		sfinfo ;

	progname = strrchr (argv [0], '/') ;
	progname = progname ? progname + 1 : argv [0] ;

	if (argc != 3)
	{
	  print_usage (progname) ;
	  return 1 ;
	} ;

	infilename = argv [1] ;
	outfilename = argv [2] ;


	memset (&sfinfo, 0, sizeof (sfinfo)) ;


	
	if (infilename [0] == '-')
	{
	  //infile=stdin;
	  /* ACK, can sndfile handle raw input??? */ 
	}
	else 	if ((infile = sf_open (infilename, SFM_READ, &sfinfo)) == NULL)
	{	printf ("Not able to open input file %s.\n", infilename) ;
		puts (sf_strerror (NULL)) ;
		return 1 ;
		} ;


	if (outfilename [0] == '-')
	  {
	    outfile = stdout;
	  } 
	else if ((outfile = fopen (outfilename, "w")) == NULL)
	{
	  printf ("Not able to open output file %s : %s\n", outfilename, sf_strerror (NULL)) ;
	  return 1 ;
	} ;	    

	  


	printf ("# Converted from file %s.\n", infilename) ;
	printf ("# Channels %d, Sample rate %d\n", sfinfo.channels, sfinfo.samplerate) ;

	//convert_to_text (infile, outfile, sfinfo.channels) ;
	find_ticks (infile, outfile, sfinfo.channels, sfinfo.samplerate) ;

	sf_close (infile) ;
	fclose (outfile) ;

	return 0 ;
} /* main */

