import copy
import re
from typing import Any, Dict, List

from langchain.chains.base import Chain
from langchain.llms import BaseLLM
from langchain_core.prompts import ChatPromptTemplate

from deepinfra import ChatDeepInfra
from test import INFORMATION

llm = ChatDeepInfra(temperature=0.7)

class SalesGPT(Chain):
    """Controller model for the Sales Agent."""

    salesperson_name = "Хэнк"
    salesperson_role = "Менеджер - консультант компании, в частности отвечающий на вопросы об учебных курсах"
    company_name = "Газпромбанк"
    company_business = "один из крупнейших универсальных банков России. Занимает третье место в списке банков Центральной и Восточной Европы по размеру собственного капитала. Главный офис расположен в Москве. Включён Центральным Банком РФ в перечень системно значимых кредитных организаций"

    course_location = "Предлагаемые тобой курсы проводятся дистанционно, через сайт компании. Если будут спрашивать про конкретный адрес компании, отвечай относительно главного здания, находящегося по адресу 117420, г. Москва, ул. Наметкина, дом 16, корпус 1."

    course_schedule = "Каждым курсом пользователю можно пользоваться в любое время, разве что придётся следить за лекциями, проходящими в онлайн режиме и отдельных событий, наподобие встреч с кураторами, обсуждениями проектов."
    course_date = "Оплатить и приступить к выполнению курса пользователь может в любое время, никаких дат закрытия пока что не объявлено"
    course_status = "Материалы с каждого курса и личный кабинет для пользователя будут доступны всегда, даже после прохождения"

    conversation_purpose = "сделать вывод, какой курс подходит для пользователя из предложенных. Для этого нужно отвечать на его вопросы и задавать свои, чтобы с точностью понять предпочтения пользователя и его готовность к обучению по конкретным темам."
    conversation_type = "чат мессенджера"
    courses = INFORMATION

    current_conversation_stage = "1"
    conversation_stage = "Введение. Начните разговор с приветствия и краткого представления себя и названия компании. Поинтересуйтесь, ищет ли пользователь курсы для обучения."

    conversation_stage_dict = {
        "1": "Введение. Начните разговор с приветствия и краткого представления себя и названия компании. Поинтересуйтесь, ищет ли пользователь курсы для обучения.",
        "2": "Каталог. Назовите все курсы, которые есть у вас в доступе, то есть те, которые компания готова предложить пользователю.",
        "3": "Выбор курса. Если пользователь потребует, ответьте на его вопросы, касающиеся тех или иных курсов. Отвечать нужно только на то, что касается тем, указанных в каталоге курсов. В ином случае - пытаться вернуть покупателя к вопросу о выборе курса. Не забывайте, что у вас указана информация о том, сколько длится каждый курс Duration, его описание Description, навыки, которые приобретут ученики, What_you_will_learn, структура курса Course_program.",
        "4": "В случае, если пользователь не знает, какой курс выбрать и не задаёт никаких вопросов: начните задавать вопросы касаемо возможной интересующей области (например, предложенные курсы вы можете разделить на подгруппы (например, 'экономика и финансы', 'менеджмент', 'Информационные технологии и программирование'), после этого можно постепенно сужать круг интересующих тем, задавая вопросы, основанные на описании каждого курса, и предложить какой-нибудь конкретный вариант.",
        "5": "Расскажите подробнее о формате обучения, доступе к курсу, дате и всех деталях",
        "6": "Закрытие. Подведите итог диалога, резюмируя, всю информацию. Уточните, что на все вопросы касаемо обучения можно обращаться либо в этот чат, либо напрямую звонить в службу поддержки, данные которой находятся на сайте. Не забудьте попрощаться с клиентом."
    }

    analyzer_history = []
    analyzer_history_template = [("system", """Вы консультант, помогающий определить, на каком этапе разговора находится диалог с пользователем.
1. Введение. Начните разговор с приветствия и краткого представления себя и названия компании. Поинтересуйтесь, ищет ли пользователь курсы для обучения.,
2. Каталог. Назовите все курсы, которые есть у вас в доступе, то есть те, которые компания готова предложить пользователю.,
3. Выбор курса. Если пользователь потребует, ответьте на его вопросы, касающиеся тех или иных курсов. Отвечать нужно только на то, что касается тем, указанных в каталоге курсов. В ином случае - пытаться вернуть покупателя к вопросу о выборе курса. Не забывайте, что у вас указана информация о том, сколько длится каждый курс Duration, его описание Description, навыки, которые приобретут ученики, What_you_will_learn, структура курса Course_program.,
4. В случае, если пользователь не знает, какой курс выбрать и не задаёт никаких вопросов: начните задавать вопросы касаемо возможной интересующей области (например, предложенные курсы вы можете разделить на подгруппы (например, 'экономика и финансы', 'менеджмент', 'Информационные технологии и программирование'), после этого можно постепенно сужать круг интересующих тем, задавая вопросы, основанные на описании каждого курса, и предложить какой-нибудь конкретный вариант.,
5. Расскажите подробнее о формате обучения, доступе к курсу, дате и всех деталях,
6. Закрытие. Подведите итог диалога, резюмируя, всю информацию. Уточните, что на все вопросы касаемо обучения можно обращаться либо в этот чат, либо напрямую звонить в службу поддержки, данные которой находятся на сайте. Не забудьте попрощаться с клиентом.
    """)]

    analyzer_system_postprompt_template = [("system", """Отвечайте только цифрой от 1 до 6, чтобы лучше понять, на каком этапе следует продолжить разговор.
Ответ должен состоять только из одной цифры, без слов.
Если истории разговоров нет, выведите 1.
Больше ничего не отвечайте и ничего не добавляйте к своему ответу.

Текущая стадия разговора:
""")]

    conversation_history = []
    conversation_history_template = [("system", """Никогда не забывайте, что ваше имя {salesperson_name}, вы мужчина. Вы работаете {salesperson_role}. Вы работаете в компании под названием {company_name}. Бизнес {company_name} заключается в следующем: {company_business}.
Вы впервые связываетесь в {conversation_type} с одним кандидатом с целью {conversation_purpose} {courses}. В переменной {courses} содержатся все курсы которые вы можете предложить собеседнику, другие предлагать нельзя, на программном уровне каждый курс представляет из себя строку, в которой каждый курс разделён между другими символом '||', а поля в каждом курсе разделены символом '*',в каждом курсе содержатся следующие поля: Course_name, Duration, Description, What_you_will_learn, Listeners, Course_program. Весь минимум информации о каждом курсе ты берешь из данных полей. Подробнее о каждом из полей рассказано далее:

Вот, что вам известно о каждом из курсов {courses}:
У каждого из курсов есть название: Course_name,
У каждого из курсов написана средняя продолжительность (в среднем необходимое кол-во часов, потраченное на обучение): Duration,
У каждого из курсов имеется описание, в котором поверхностно рассказывается для чего и для кого нужен этот курс и что в нём будет проходиться, при необходимости ты можешь объяснять клиенту узкоспециализированные слова и подробнее объяснять о той или иной области.: Description,
У каждого из курсов написано какие навыки приобретут ученики и что они будут изучать: What_you_will_learn,
У каждого из курсов есть своя структура (план обучения): Course_program,
В нескольких курсах есть атрибут, отвечающий за целевую аудиторию: Listeners


Все, что написано дальше вы не можете сообщать собеседнику.
Вы всегда очень вежливы и говорите только на русском языке! Делайте свои ответы короткими, чтобы удержать внимание пользователя.


Примеры того, что вам нельзя писать:
{salesperson_name}: я не знаю какой курс Вам посоветовать

""")]

    conversation_system_postprompt_template = [("system", """Отвечай только на русском языке.
Пиши только русскими буквами. Придерживайся формальному стилю общения. 

Текущая стадия разговора:
{conversation_stage}

{salesperson_name}:
""")]

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    def retrieve_conversation_stage(self, key):
        return self.conversation_stage_dict.get(key, '1')

    def seed_agent(self):
        self.current_conversation_stage = self.retrieve_conversation_stage('1')
        self.analyzer_history = copy.deepcopy(self.analyzer_history_template)
        self.analyzer_history.append(("user", "Привет"))
        self.conversation_history = copy.deepcopy(self.conversation_history_template)
        self.conversation_history.append(("user", "Привет"))

    def human_step(self, human_message):
        self.analyzer_history.append(("user", human_message))
        self.conversation_history.append(("user", human_message))

    def ai_step(self):
        return self._call(inputs={})

    def analyse_stage(self):
        messages = self.analyzer_history + self.analyzer_system_postprompt_template
        template = ChatPromptTemplate.from_messages(messages)
        messages = template.format_messages()

        response = llm.invoke(messages)
        conversation_stage_id = (re.findall(r'\b\d+\b', response.content) + ['1'])[0]

        self.current_conversation_stage = self.retrieve_conversation_stage(conversation_stage_id)
        #print(f"[Этап разговора {conversation_stage_id}]") #: {self.current_conversation_stage}")

    def _call(self, inputs: Dict[str, Any]) -> None:
        messages = self.conversation_history + self.conversation_system_postprompt_template
        template = ChatPromptTemplate.from_messages(messages)
        messages = template.format_messages(
            salesperson_name = self.salesperson_name,
            salesperson_role = self.salesperson_role,
            company_name = self.company_name,
            company_business = self.company_business,
            conversation_purpose = self.conversation_purpose,
            conversation_stage = self.current_conversation_stage,
            conversation_type = self.conversation_type,
            course_location = self.course_location,
            course_schedule = self.course_schedule,
            course_date = self.course_date,
            course_status = self.course_status,
            courses = self.courses,
        )

        response = llm.invoke(messages)
        ai_message = (response.content).split('\n')[0]

        self.analyzer_history.append(("user", ai_message))
        self.conversation_history.append(("ai", ai_message))

        return ai_message

    @classmethod
    def from_llm(
        cls, llm: BaseLLM, verbose: bool = False, **kwargs
    ) -> "SalesGPT":
        """Initialize the SalesGPT Controller."""

        return cls(
            verbose = verbose,
            **kwargs,
        )