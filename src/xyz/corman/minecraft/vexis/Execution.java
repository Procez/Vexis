package xyz.corman.minecraft.vexis;

import java.util.Set;

import org.bukkit.entity.Player;
import org.bukkit.event.Event;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.inventory.Inventory;
import org.python.core.Py;
import org.python.core.PyDictionary;
import org.python.core.PyException;
import org.python.core.PyBaseException;
import org.python.core.PyList;
import org.python.core.PyObject;
import org.python.core.PyString;
import org.python.core.PyTuple;
import org.python.util.PythonInterpreter;

public class Execution {
	PythonInterpreter vexisInterpreter;
	PyObject mod;
	
	public Execution(PythonInterpreter vexisIntrp, PyObject module) {
		vexisInterpreter = vexisIntrp;
		mod = module;
	}
	
    public void handleCall(PyObject func, PyObject[] args) {
    	try {
    		func.__call__(args);
    	} catch (Exception e) {
    		showError(e);
    	}
    }
    
	public boolean runCommand(PyObject func, Player sender, String label, String[] args) {
		try {
			func.__call__(
					Py.java2py(sender),
					Py.java2py(label),
					Py.java2py(args)
			);
		} catch (Exception e) {
			showError(e);
		}
		return true;
	}
	
	public void showError(Object excep) {
		if (excep == null) {
			return;
		} else if (excep instanceof PyException) {
			PyException e = (PyException) excep;
			e.printStackTrace();
		} else if (excep instanceof Exception) {
			Exception exception = (Exception) excep;
			exception.printStackTrace();
		}
	}
	
	public void handleEvent(Event event) {
		try {
			PyDictionary _events = (PyDictionary) vexisInterpreter.get("vexis").__getattr__("_events");
			Set<PyObject> _eventset = _events.pyKeySet();
			PyList guis = (PyList) mod.__getattr__("guis");
			if (event instanceof InventoryClickEvent) {
				InventoryClickEvent invEvent = (InventoryClickEvent) event;
				Inventory inv = invEvent.getClickedInventory();
				int slot = invEvent.getSlot();
				for (Object _gui : guis) {
					PyObject gui = (PyObject) _gui;
					Inventory _inv = (Inventory) gui.__getattr__("inv").__tojava__(Inventory.class);
					if (_inv != inv) {
						continue;
					}
					PyDictionary callbacks = (PyDictionary) gui.__getattr__("callbacks");
					for (PyObject _slot : callbacks.pyKeySet()) {
						PyTuple value = (PyTuple) callbacks.get(_slot);
						PyObject function = (PyObject) value.get(0);
						boolean movable = (boolean) value.get(1);
						int py_slot = (int) _slot.__tojava__(int.class);
						if (py_slot != slot) {
							continue;
						}
						if (!movable) {
							invEvent.setCancelled(true);
						}
						if (!(function == null)) {
							try {
								function.__call__(Py.java2py(event));
							} catch (PyException e) {
								showError(e);
							}
						}
					}
				}
			}
			for (PyObject _key : _eventset) {
				PyString eventName = (PyString) _key;
				PyList eventCall = (PyList) _events.get(eventName);
				String evname = event.getEventName().trim().toLowerCase();
				String evneeded = eventName.toString().trim().toLowerCase();
				//Class<? extends Event> cls = eventlist.get(eventName.toString());
				//System.out.println(evcls.toString() + " || "  + evneeded.toString());
				if ( evname.equals(evneeded) ) {
				//if (evneeded.isAssignableFrom(evcls)) {
					PyObject pyEvent = Py.java2py(event);
					for (PyObject func : eventCall.getArray()) {
						try {
							func.__call__(pyEvent);
						} catch (PyException e) {
							showError(e);
						}
					}
				}
			}
			
		} catch (Exception e) {
			showError(e);
		}
	}
}
