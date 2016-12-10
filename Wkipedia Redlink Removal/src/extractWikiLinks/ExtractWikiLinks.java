package extractWikiLinks;

import java.io.IOException;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobClient;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;


public class ExtractWikiLinks {
	
	public static class LinkMapper extends MapReduceBase implements Mapper<Object, Text, Text, Text>{
	
	   public void map(Object key, Text value, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
	       
		    String title = "";
	        String page = value.toString();
	        int startTitle = page.indexOf("<title>") + "<title>".length();
	        int endTitle = page.indexOf("</title>");
	        title = page.substring(startTitle, endTitle).replace(" ", "_");
	       
	        int startText = page.indexOf("<text");
	        int endText = page.indexOf("</text>");
	        String text = "";
	        
	        if ( startText != -1 && endText != -1){
	            text = page.substring(startText, endText);
	        }
	        output.collect(new Text(title), new Text("@@"));
	        Pattern pattern = Pattern.compile("\\[\\[(.*?)\\]\\]");
	        
	        Matcher matcher = pattern.matcher(text);
	        while(matcher.find()) {
	            String patternMatch = matcher.group(1);
	            extractOutput(output, title, patternMatch);
	        }
	    }

		private void extractOutput(OutputCollector<Text, Text> output, String title, String patternMatch)
				throws IOException {
			if(patternMatch != null && !patternMatch.isEmpty()){
			    if(patternMatch.contains("|")){
			    	int indexOfPipe = patternMatch.indexOf("|");
			    	String nextLink = patternMatch.substring(0, indexOfPipe);
			        nextLink = nextLink.replace(" ", "_");
			        fillOutput(output, title, nextLink);
			    }else{
			        String nextLink = patternMatch.replace(" ","_");
			        fillOutput(output, title, nextLink);
			    }
			}
		}

		private void fillOutput(OutputCollector<Text, Text> output, String title, String nextLink) throws IOException {
			if ( !nextLink.equals(title)){
			    output.collect( new Text(nextLink), new Text(title) );
			}
		}
	}
	
	 public static class LinkReducer extends MapReduceBase implements Reducer<Text, Text, Text, Text> {
	
	   public void reduce(Text key, Iterator<Text> values, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
		    int idx = 0 ;
	        Set<String> links = new HashSet<String>();
	        
	        while (values.hasNext()){
	            links.add(values.next().toString());
	            idx++;
	        }
            if (links.contains("@@")){
                retrieveReducedLinks(key, output, links);
            }
	    }

		private void retrieveReducedLinks(Text key, OutputCollector<Text, Text> output, Set<String> links) throws IOException {
			Iterator<String> i = links.iterator();
			while(i.hasNext()){
			    String nextIdxOfLink = (String) i.next();
			    if (!nextIdxOfLink.equals("@@"))
			        output.collect(new Text(nextIdxOfLink), key);
			    else {
			        output.collect(key, new Text("@@"));
			    }
			}
		}
	 }
	
	 public static class GraphMapper extends MapReduceBase implements Mapper<LongWritable, Text, Text, Text> {
		    public void map(LongWritable key, Text value, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
		        String[] splits = value.toString().split("\t");
		        output.collect(new Text(splits[0]), new Text(splits[1]));
		    }
		}
	 
	 public static class GraphReducer extends MapReduceBase implements Reducer<Text, Text, Text, Text> {
		    public void reduce(Text key, Iterator<Text> values, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
		        
		    	StringBuffer sb = new StringBuffer();
		        if (key.toString().equals("@@")){
		            while(values.hasNext()){
		                output.collect(new Text(values.next()), new Text(""));
		            }
		        }else{
		            collectValues(values, sb);
		            sb = new StringBuffer(sb.toString().trim());
		            output.collect(key, new Text(sb.toString()));
		        }
		    }

			private void collectValues(Iterator<Text> values, StringBuffer sb) {
				while(values.hasNext()){
				    String linked = values.next().toString();
				    if ( !linked.equals("@@")){
				        sb.append(linked + "\t");
				    }
				}
			}
		}
	 
	public static void main(String[] args) throws Exception {
		ExtractWikiLinks wikiLinks = new ExtractWikiLinks();

        String input=args[0];
        String output=args[1];
        String tempFolder = output + "/temp/";
        String graphFolder = output + "/graph/";
        wikiLinks.linkgenerator(input, tempFolder);
        wikiLinks.graphGenerator(tempFolder, graphFolder);
	  }
	
    public void linkgenerator(String input, String output) throws IOException {
        JobConf conf = new JobConf(ExtractWikiLinks.class);

        FileInputFormat.setInputPaths(conf, new Path(input));
        
        conf.setInputFormat(XMLInputFormat.class);
        conf.set(XMLInputFormat.START_TAG_KEY, "<page>");
        conf.set(XMLInputFormat.END_TAG_KEY, "</page>");
        conf.setMapperClass(LinkMapper.class);

        FileOutputFormat.setOutputPath(conf, new Path(output));
        conf.setReducerClass(LinkReducer.class);

        conf.setOutputKeyClass(Text.class);
        conf.setOutputValueClass(Text.class);

        JobClient.runJob(conf);
    }
    
    public void graphGenerator(String input, String output) throws IOException {
        JobConf conf = new JobConf(ExtractWikiLinks.class);
        
        FileInputFormat.setInputPaths(conf, new Path(input));
        FileOutputFormat.setOutputPath(conf, new Path(output));
        
        conf.setJarByClass(ExtractWikiLinks.class);
        
        conf.setMapperClass(GraphMapper.class);
        conf.setReducerClass(GraphReducer.class);

        conf.setOutputKeyClass(Text.class);
        conf.setOutputValueClass(Text.class);

        JobClient.runJob(conf);
    }
    
    /**
     * 
     * Understanding Reference from Git-WikipediaPagerank
     *
     */
}
