
use llm to add properies to my notes 
use llm to organize my notes
### control with voice
general -  use voice to control my pc, or only vsc, dictastion would be also good, 

### text2speach
i think i saw tools that you are talking and at the end whole text is structurized and formatted
wisprflow
superwhisper
my llm, mcp, app
can give voice commands to pc

sterowanie przegladarka 
browser use

### Graphify
Gitnexus
Test it on some project
Try to talk about this project with Agent with/without it. Is it better
Try to export it to Obsidian

### Open Claw Start
I need to host it or run locally in docker
But in general I need to connect it llm, directly or using open router

use llm to prepare news feed - filter our fakes, duplicates, keep only important news

On youtube there are planty video explaining how to use it in daily churns
- explore news and create my personal news feed
- assisst with my emails
- assists with work search

Perplexity
CodeRabbit



rate limiting
retry, circuit breaker, polly
cqrs, read model, orchastrated command, single resposibility commanfd, maybe we don't need services
dotnet aspire
kafka

verify,snapshoter

write instruction about techniques agent should you to write more performant code
- in / out/ ref
- class vs record
- span
- nolinq
- unrolling loops
- zero memory allocation
- others
- static lambda 
- regex
- optimal logs

write doc about general guidlines
- define whether null is allowed in json
- other

rest api, graphql, grpc

how to organize topics for qeueu messages sub/pub
on per message type 
other alternatives

https://github.com/github/awesome-copilot?utm_source=chatgpt.com
https://github.com/ai-boost/awesome-harness-engineering
https://github.com/VoltAgent/awesome-agent-skills
https://github.com/microsoft/azure-skills

https://medium.com/@signadot/why-staging-doesnt-scale-for-microservice-testing-98892b936c38
czesc szerszego problemu jak wdrozyc sie na staging, przetestowac swoja zmiane i niczego nie rozwalic
also: env by branch
telepresence
feature test
run localla, test in cloud
https://www.signadot.com/

mini complete app
- system to simulte how to process credit card transactiisn
- grafana / kibana 
- azure insight
- sidecars - log http requests, gather output logs
- pulumi
- aks
- graphify
- durable function workflow
- some agentic workflow - bugs, problems, private data leaks in logs
- front - react, fully responsive for backend changes  - events be => fe, (sse, push, signalr)
	- making concurrent changes in data
- test
- agentic tests = must be run by agents
- modules - feature per folder, 
- create some docs
- use graphify, github nexus for code graph
- grafana alerts
- alerts base on trends
- system altetowania i eskalacji - jak w allegro
- front poc - create front dynamically base on user promp - front per user
- e2e tests - frontend tests, playright, use ai to fix broken tests, use ai to run broken test, find button to click with llm
- how to deploy  canary, revert
- multi reviewers
- agentic workflow for development
- aks, k8s - app service to observe and basic operations
- update nugets, frameworks, dotnet, dockers, tools, etc
	- investigate what's changes, what's break, what's new 
	- propose code changes
- istio, envoy
- open telemetry
- polly - retry, cicuit breaker
- graphql
- oauth
- pipelines
- deply to k8s
- try to use some task board, and use agent is the loop as often as possible

app idea:
- olx buy/sell and earn
- expand it globally

app idea:
- very universal drilling app, maybe with ai help to wrote customized queries
- with many connectors
- idea: first level payments list, i can zoom to payment, see some structured ui for payment, but i can zoom in to see raw logs, db objects, can zoom to user, and see user card. On the other hand on user i can see list of payments, so it is more like fractal, 

app idea:
- manga / anime browser
  
 Exercises
- build modern mcp server and use it from vsc or local openai, gemini, cloude etc
- use sql mcp data api builder, check if i can talk with model about database, or use this knowledge in agent workflow
- n8n / LangGraph + LangSmith / Flowise
- wykorzystanie powyzszego do sterowania slackiem jak i w druga strone (na slacku mozna np wystawic zbior linkow albo przyciskow)
- [https://github.com/mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)

mcp server / client / stateless / alternatives / skills / commands line / how to discover  how use them in chatgpt / claude / local copilot / how flow is working when local is mixed with remote inference

leetcode
powtorka z c# pytan
wzorce projektowe
system design

https://www.aihero.dev/skills-wayfinder
i inne tam sa ciekawe rzeczy

majac jakas strone zrobic jej dokumnetacje,
zlecic analize kodu by wykryc ukryte przyciski etc, tez kodu js, nie tylko html
zrobic zmiane w dokumentacji
nakazac weryfikacje dokumentacji

agent harness
- log decyzyjny by zrozumiec jak dziala
- kilka workflowow pracujact wspolnie i nawzajem na siebie wplywajacych

process:
- agent koduje
- review na github
- inni agenvi komentuja
- ktos poprawia
- decyzja ze jest ok 
- brak konsensusu
  
agent samomodyfikujacy process
swoje skille, rules.
Albo prosciej: ma jakas baze plikowa, ktore aktualizuje

cloud agents

webmco