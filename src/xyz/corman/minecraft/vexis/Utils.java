package xyz.corman.minecraft.vexis;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Set;
import java.util.function.BiPredicate;

import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.python.core.Py;
import org.python.core.PyObject;
import org.yaml.snakeyaml.Yaml;

import xyz.corman.minecraft.vexis.Execution;

public class Utils {
    public interface Function {
    	public Object call();
    }
	
	public static Entity getNearestEntityInSight(Player player, int range) {
	    ArrayList<Entity> entities = (ArrayList<Entity>) player.getNearbyEntities(range, range, range);
	    ArrayList<Block> sightBlock = (ArrayList<Block>) player.getLineOfSight( (Set<Material>) null, range);
	    ArrayList<Location> sight = new ArrayList<Location>();
	    for (int i = 0;i<sightBlock.size();i++)
	        sight.add(sightBlock.get(i).getLocation());
	    for (int i = 0;i<sight.size();i++) {
	        for (int k = 0;k<entities.size();k++) {
	            if (Math.abs(entities.get(k).getLocation().getX()-sight.get(i).getX())<1.3) {
	                if (Math.abs(entities.get(k).getLocation().getY()-sight.get(i).getY())<1.5) {
	                    if (Math.abs(entities.get(k).getLocation().getZ()-sight.get(i).getZ())<1.3) {
	                        return entities.get(k);
	                    }
	                }
	            }
	        }
	    }
	    return null; //Return null/nothing if no entity was found
	}
	
	public static void createExplosion(Location loc, float power, boolean fire, boolean blockbreak) {
		loc.getWorld().createExplosion(loc, power, fire, blockbreak);
	}
	
	public static BiPredicate<?, ?> pyFuncToBiPredicate(Execution execution, PyObject func) {
		return (x, y) -> {
			PyObject out;
			try {
				out = func.__call__(Py.java2py(x), Py.java2py(y));
			} catch (Exception e) {
				execution.showError(e);
				return false;
			}
			Object output = out.__tojava__(Object.class);
			if (output instanceof Boolean) {
				return (boolean) output;
			} else {
				return false;
			}
		};
	}
	
	//PacketPlayOutCustomPayload packet;
	
    static String stripExtension (String str) {
        // Handle null case specially.

        if (str == null) return null;

        // Get position of last '.'.

        int pos = str.lastIndexOf(".");

        // If there wasn't any '.' just return the string as is.

        if (pos == -1) return str;

        // Otherwise return the string, up to the dot.

        return str.substring(0, pos);
    }
    
    public static Object load_yaml(Yaml yaml, String string) {
    	Object out = yaml.load(string);
    	return out;
    }
    
    public <T> T call_generic(Function func, Class<T> type) {
    	Object output = func.call();
    	return type.cast(output);
    }
	
	public static String replaceColors(String string){
		return string.replaceAll("(?i)&([a-n0-9])", "\u00A7$1");
	}
	
	public String read_buffered(BufferedReader br) {
	    StringBuffer line = new StringBuffer();


	    try { 
	        while(br.ready()) {
	        	line.append("\n" + br.readLine());
	        }
	    } catch(IOException e){
	        e.printStackTrace();
	    }

	    return line.toString();
	}
	
	public static Iterable<Object> load_yml(Yaml yaml, String string) {
		return yaml.loadAll(string);
	}
	
	public static InputStream stringToStream(String string) {
		return new ByteArrayInputStream(string.getBytes());
	}
}
