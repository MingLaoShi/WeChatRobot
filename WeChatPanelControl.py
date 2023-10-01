from uiautomation import WindowControl
import logging


class WeCahtPanelControl:
    def __init__(self, logger) -> None:
        self.window = WindowControl(Name="微信")
        self.window.SetActive()
        self.logger = logger
        self.group_panel = self.find_group_list_panel()
        self.chat_panel = self.find_chat_list_panel()
        # self.chat_list=self.chat_panel.GetChildren()[0]

    def get_chat_list(self, chat_panel):
        child = chat_panel.GetChildren()
        # if len(child)>1:
        #     return child[1]
        # else:
        #     return child[0]
        return child

    def find_group_list_panel(self):
        panel = self.window.GetChildren()[2]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[1]

    def find_input_box_panel(self):
        panel = self.window.GetChildren()[2]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[2]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[1]
        panel = panel.GetChildren()[1]

    def find_chat_list_panel(self):
        panel = self.window.GetChildren()[2]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[2]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[1]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[0]
        panel = panel.GetChildren()[0]
        return panel

    def get_message_from_panel(self, panel):
        message = panel.Name
        child = panel.GetChildren()[0]
        sender = ""
        if len(child.GetChildren()) > 2:
            sender_others = child.GetChildren()[0].Name
            sender_me = child.GetChildren()[2].Name
            if sender_others != "":
                sender = sender_others
            else:
                sender = sender_me
        else:
            sender = "otherPanel"
        return (sender, message)


def test():
    control = WeCahtPanelControl(logging)
    control.find_chat_list_panel()


if __name__ == "__main__":
    test()
