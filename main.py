from app import Application
from controller.manager import PayrollManager
from view.view import View

if __name__ == "__main__":
    view = View()
    manager = PayrollManager()
    manager.init_test_data()

    app = Application(view, manager)
    app.run()
