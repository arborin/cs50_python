from project import get_device_list, menu_options, write_device_list, add_device, del_device, write_device_list, clear_screen


def test_get_device_list():
    assert isinstance(get_device_list(), list)
    assert len(get_device_list()) >= 0
    
def test_menu_options():
    menu = menu_options()
    assert menu['1'] == "Device List"
    assert menu['2'] == "Add Device"
    assert menu['3'] == "Del Device"
    assert menu['4'] == "Make Backup"
    assert menu['5'] == "Exit"
    
    
def test_add_device():
    assert  add_device('Router', '192.168.1.1', True) >= 0

def test_del_device():  
    assert del_device(1, True) == 1
   
    
def test_write_device_list():
    assert write_device_list() == True
    
def test_clear_screen():
    assert clear_screen() == True
    

if __name__ == "__main__":
    test_get_device_list()
    test_menu_options()
    test_add_device()
    test_del_device()
    test_write_device_list()
    test_clear_screen()
    
    
    


