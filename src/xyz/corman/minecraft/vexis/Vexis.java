package xyz.corman.minecraft.vexis;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;

import org.bukkit.Bukkit;
import org.bukkit.event.Event;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.server.PluginEnableEvent;
import org.bukkit.plugin.EventExecutor;
import org.bukkit.plugin.Plugin;
import org.bukkit.plugin.PluginManager;
import org.bukkit.plugin.RegisteredListener;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitRunnable;
import org.python.core.CompilerFlags;
import org.python.core.Py;
import org.python.core.PyException;
import org.python.core.PyList;
import org.python.core.PyModule;
import org.python.core.PyObject;
import org.python.core.PyString;
import org.python.util.PythonInterpreter;

import io.github.classgraph.ClassGraph;
import io.github.classgraph.ClassInfo;
import io.github.classgraph.ClassInfoList;
//import net.minecraft.server.v1_14_R1.MinecraftKey;
//import net.minecraft.server.v1_14_R1.PacketPlayOutCustomPayload;
//import net.minecraft.server.v1_14_R1.PacketDataSerializer;

public class Vexis extends JavaPlugin implements Listener {
	
	static HashMap<String, PythonInterpreter> interpreters;
	static HashMap<String, Class<? extends Event>> eventlist = new HashMap<String, Class<? extends Event>>();
	private PythonInterpreter vexisInterpreter;
	static PyObject mod;
	RegisteredListener registeredListener;
	static String vexis_scripts;
	static String vexis_externals;
	static PyObject errorHandler;
	static PluginManager plugmanager = Bukkit.getPluginManager();
	static File plugin_folder;
	static ArrayList<File> externals;
	Listener listener = new Listener() {};
	
	static Execution execution;
	
	EventExecutor executor = (ignored, event) -> execution.handleEvent(event);
	
	@SuppressWarnings("unchecked")
	@EventHandler
	public void onPluginEnable(PluginEnableEvent e) {
		Plugin plugin = e.getPlugin();
		String _package = plugin.getClass().getPackage().getName();
    	ClassInfoList events = new ClassGraph()
    	        .enableClassInfo()
    	        .scan() //you should use try-catch-resources instead
    	        .getClassInfo(Event.class.getName())
    	        .getSubclasses()
    	        .filter(info -> !info.isAbstract())
    	        .filter(info -> _package.startsWith(info.getPackageInfo().getName()));
    	try {
    	    for (ClassInfo event : events) {
    	        Class<? extends Event> eventClass = (Class<? extends Event>) Class.forName(event.getName());
    	   
    	        eventlist.put(event.getName(), eventClass);
    	        
    	        if (Arrays.stream(eventClass.getDeclaredMethods()).anyMatch(method ->
    	                method.getParameterCount() == 0 && method.getName().equals("getHandlers"))) {
    	            //We could do this further filtering on the ClassInfoList instance instead,
    	            //but that would mean that we have to enable method info scanning.
    	            //I believe the overhead of initializing ~20 more classes
    	            //is better than that alternative.
    	       
    	            Bukkit.getPluginManager().registerEvent(eventClass, listener,
    	                    EventPriority.NORMAL, executor, this);
    	        }
    	    }
    	} catch (ClassNotFoundException exception) {
    	    throw new AssertionError("Scanned class wasn't found", exception);
    	}
	}
	
	public static boolean runScript(Object script_data) {
		if (script_data instanceof String) {
			script_data = new File((String) script_data);
		}
		File script = (File) script_data;
		String scriptname = script.toString();
		String name = Utils.stripExtension(new File(vexis_scripts).toURI().relativize(script.toURI()).getPath());
		System.out.println("[Vexis] Loading script: " + name);
		String basename = Utils.stripExtension(script.getName());
		String content;
		try {
			content = new String(Files.readAllBytes(Paths.get(scriptname)));
		} catch (IOException e) {
			return false;
		}
		PythonInterpreter interpreter = new PythonInterpreter() {
			{
				cflags = new CompilerFlags(CompilerFlags.PyCF_SOURCE_IS_UTF8);
			}
        };
        
    	PyList path = interpreter.getSystemState().path;
        
        for (File file : externals) {
	        path.append(new PyString(file.toPath().toString()));
        }
	        	
		interpreter.set("__name", (PyObject) new PyString(basename));
		interpreter.set("vexis", mod);
		interpreter.set("color", mod.__getattr__("color"));
		InputStream stream = Utils.stringToStream(content);
		new BukkitRunnable() {
			public void run() {
				try {
					interpreter.execfile(stream, script.toString());
				} catch (PyException e) {
					execution.showError(e);
				}
			}
		}.run();
		interpreters.put(name, interpreter);	
		
		mod.__getattr__("modules").__setitem__(name, new PyModule(name, interpreter.getLocals()));
		
		return true;
	}
	
	public static boolean endScript(Object intrp) {
		if (intrp instanceof String) {
			intrp = interpreters.get(intrp);
		}
		PythonInterpreter interpreter = (PythonInterpreter) intrp;
		try {
			interpreter.close();
			interpreters.values().removeAll(Collections.singleton(interpreter));
		} catch (Exception e) {
			return false;
		}
		return true;
	}
	
	public static String reloadScript(String script) {
		if (!interpreters.containsKey(script)) {
			boolean end = endScript(script);
			if (!end) {
				return "The script could not be disabled.";
			}
		}
		boolean run = runScript(script);
		if (!run) {
			return "The script could not be executed.";
		}
		return "The script was executed successfully.";
	}
		
    @SuppressWarnings("unchecked")
	@Override
    public void onEnable() {
    	String vexis_folder = getDataFolder().getAbsolutePath();
    	vexis_scripts = Paths.get(vexis_folder, "scripts").toString();
    	vexis_externals = Paths.get(vexis_folder, "external").toString();
    	System.out.println("[Vexis] Checking if configuration is setup at " + vexis_folder);
    	plugin_folder = getDataFolder().getParentFile();
        File vexisfolder = new File(vexis_folder);
        File vexisexternals = new File(vexis_externals);
        File vexisscripts = new File(vexis_scripts);
        
        InputStream in = getClass().getResourceAsStream("vexis.py");
        
        if (in == null) {
        	in = getClass().getResourceAsStream("./vexis.py");
        }
        if (in == null) {
        	System.out.println("in == null");
        }

        //InputStreamReader rd = new InputStreamReader(in);
        //BufferedReader reader = new BufferedReader(rd);
        //vexisText = read_buffered(reader);

        externals = new ArrayList<File>();
        
        File[] plugin_files = plugin_folder.listFiles();
        if (plugin_files != null) {
        	for (File plugin : plugin_files) {
        		String filename = plugin.toPath().getFileName().toString();
        		if (filename.endsWith(".jar")) {
        			externals.add(plugin);
        		}
        	}
        }
        
        File[] external_files = vexisexternals.listFiles();
        if (external_files != null) {
        	for (File external : external_files) {
        		String filename = external.toPath().getFileName().toString();
        		if (filename.endsWith(".jar")) {
        			externals.add(external);
        		}
        	}
        }
       
        vexisInterpreter = new PythonInterpreter();
    	PyList path = vexisInterpreter.getSystemState().path;
        
        for (File file : externals) {
	        path.append(new PyString(file.toPath().toString()));
        }
        
        try {
        	vexisInterpreter.execfile(in, Paths.get(this.getFile().getAbsoluteFile().toString(), "bin", "vexis.py").toString());
        } catch (Exception e) {
        	execution.showError(e);
        }
        mod = vexisInterpreter.get("vexis");
        mod.__setattr__("_vexis_data_folder", new PyString(getDataFolder().getAbsolutePath()));
        mod.__setattr__("_vexis_scripts", new PyString(vexis_scripts));
        mod.__setattr__("_vexis_folder", new PyString(vexis_folder));
    	execution = new Execution(vexisInterpreter, mod, eventlist);
    	mod.__setattr__("_vexis_execution", Py.java2py(execution));
        try {
        	mod.__getattr__("document").__call__();
        } catch (Exception e) {
        	execution.showError(e);
        }
        
        if (! vexisfolder.exists()){
            vexisfolder.mkdir();
        }
        if (! vexisscripts.exists()) {
        	vexisscripts.mkdir();
        }
        
        if (! vexisexternals.exists()) {
        	vexisexternals.mkdir();
        }
        
        File[] scripts = vexisscripts.listFiles();
		interpreters = new HashMap<String, PythonInterpreter>();
        if (scripts != null) {
        	for (File script : scripts) {
        		runScript(script);
        	}
        }
    	System.out.println("[Vexis] Vexis has been enabled.");

    	ClassInfoList events = new ClassGraph()
    	        .enableClassInfo()
    	        .scan() //you should use try-catch-resources instead
    	        .getClassInfo(Event.class.getName())
    	        .getSubclasses()
    	        .filter(info -> !info.isAbstract());

    	try {
    	    for (ClassInfo event : events) {
    	        Class<? extends Event> eventClass = (Class<? extends Event>) Class.forName(event.getName());
    	   
    	        eventlist.put(event.getName(), eventClass);
    	        
    	        if (Arrays.stream(eventClass.getDeclaredMethods()).anyMatch(method ->
    	                method.getParameterCount() == 0 && method.getName().equals("getHandlers"))) {
    	            //We could do this further filtering on the ClassInfoList instance instead,
    	            //but that would mean that we have to enable method info scanning.
    	            //I believe the overhead of initializing ~20 more classes
    	            //is better than that alternative.
    	       
    	            Bukkit.getPluginManager().registerEvent(eventClass, listener,
    	                    EventPriority.NORMAL, executor, this);
    	        }
    	    }
    	} catch (ClassNotFoundException e) {
    	    throw new AssertionError("Scanned class wasn't found", e);
    	}
    	
    }
    
    @Override
    public void onDisable() {
    	try {
	    	for (PythonInterpreter interpreter : interpreters.values()) {
	    		endScript(interpreter);
	    	}
    	} catch (Exception e) {}
    	System.out.println("[Vexis] Vexis has been disabled.");
    }

	
}