None selected 

Skip to content
Using Gmail with screen readers
20 of 258,043
The KV Cache Wars?
Inbox

Ken Huang from Agentic AI <kenhuangus@substack.com> Unsubscribe
11:37 AM (3 hours ago)
to me


Forwarded this email? Subscribe here for more
The KV Cache Wars?
Ken Huang
Apr 6
∙
Preview

 




READ IN APP
 
Something quiet but consequential is happening beneath the surface of Agentic AI infrastructure. While the discourse tends to focus on benchmark scores and reasoning capabilities, a different battle has been raging in frontier research labs, GPU memory hierarchies, and conference proceedings: the war over the KV cache.


This battle matters because it defines the boundary of what agentic AI can actually do. Context windows measured in millions of tokens, always-on agents that maintain memory across days of interaction, multi-model pipelines coordinating across workloads — none of these work at scale without solving the memory problem that sits at the center of transformer inference. That problem is the key-value cache.

This blog post cover the following topics


The Core Problem
Every decoder-only transformer model — GPT, Llama, Gemini, DeepSeek, all of them — generates text autoregressively. Each new token attends to every previous token in the context. Without caching, this requires recomputing the key and value matrices for every prior token on every single forward pass. The compute cost is quadratic in context length: double the context, quadruple the computation.

The KV cache solves this by storing those key and value projections in memory so they never need to be recomputed. This is the right trade — swapping compute cost for memory cost. But the trade has limits. The KV cache grows linearly with context length, linearly with the number of transformer layers, linearly with batch size, and linearly with the number of key-value heads. At a 128K context window on a 70B-parameter model, that linear growth adds up to roughly 42 gigabytes of KV cache memory alone — leaving almost nothing for model weights on an 80 GB card.

The situation breaks down across two stages of inference in distinct ways. During prefill, where the model ingests the entire prompt at once, a large context demands an enormous immediate block of compute and memory, slowing time-to-first-token. During decode, where the model generates new tokens one by one, the sheer resident size of the KV cache creates memory bandwidth pressure that caps throughput — the GPU is often waiting on memory reads, not compute.

As agentic workflows have grown more common and context windows have extended toward millions of tokens, these two bottlenecks have merged into a single architectural challenge that the entire industry is attacking simultaneously from different angles. The approaches fall into three broad families: reducing what gets stored through eviction and sparse attention, compressing what gets stored through quantization and dimensionality reduction, and rethinking where context lives through hierarchical memory and hardware innovation.

Before evaluating any optimization strategy, it helps to have a precise mental model of the four layers that sit between a user’s prompt and a generated token. Each layer has its own failure mode, its own memory budget, and its own relationship to the layers above and below it. Conflating them is the most common reason engineers reach for the wrong tool.


The context window: a growing sequence of decisions
Every token the model has ever seen in the current session lives in the context window. Tokens arrive left to right — the prompt first, then each newly generated token appended to the right edge — and the window grows by exactly one position with each generation step. There is no forgetting, no summarization, no compression happening at this layer. The context window is simply the authoritative ordered record of the conversation so far.

What makes the context window architecturally important is that the current query token — the token the model is about to predict past — must compute its relationship to every prior token in that sequence. This is not a design choice that can be relaxed without changing the model’s fundamental behavior. Attention is defined as a function of the current query against all prior keys and values. The query token drives all downstream computation; every other token in the window is a passive participant being looked up.

As the context grows, so does the computational cost of that lookup — quadratically under naive full attention, and linearly in memory regardless of the attention strategy. A 128K-token context is not eight times more expensive than a 16K context in some abstract sense: it requires eight times as much KV cache storage, and under full attention it requires 64 times as much attention computation. These two costs scale differently, which is why eviction strategies (which attack compute) and compression strategies (which attack memory) solve different parts of the same problem.

The KV cache: two matrices that remember everything
When the transformer processes the context, it projects every token’s embedding into three vectors: a query (Q), a key (K), and a value (V). The query is used only for the current step and discarded. The key and value vectors, however, need to be available at every future step — because every future query token will need to attend over them. Recomputing them from scratch on each step would cost as much as running the entire forward pass again for every prior token, which is prohibitively expensive at scale...

Keep reading with a 7-day free trial
Subscribe to Agentic AI to keep reading this post and get 7 days of free access to the full post archives.

Start trial
A subscription gets you:
Subscriber-only posts and full archive
Post comments and join the community
Yealy subscriber can book 30 minutes virtual meeting with me by sending me an email.
 
Like
Comment
Restack
 
© 2026 ken
University of San Francisco, San Francisco, CA 94104
Unsubscribe

Start writing



Compose:
New Message
MinimizePop-outClose


Forwarded this email? Subscribe here for more
What Andrej Karpathy Got Right: How a Local LLM Wiki Beats RAG? How do we leverage the latest Google Gemma 4 models for local intelligence?
Ken Huang
Apr 5
∙
Preview

 




READ IN APP
 
In a recent gist, Andrej Karpathy articulated a vision that resonates deeply with anyone drowning in a sea of raw information. The core insight? Conventional RAG is fundamentally transient. Every time you ask a question, the LLM rediscovers knowledge from scratch. There is no accumulation. No compounding. No persistent artifact that grows richer with every source you read.

The solution is a persistent, LLM-maintained wiki — a structured, interlinked collection of markdown files that sits between you and your raw sources.

“There is no accumulation. No compounding. No persistent artifact that grows richer with every source you read.”

The Vision: Manual Ingestion as Current Best Practice
Karpathy suggests that the highest-fidelity way to build such a system is through manual ingestion. You read a paper, you discuss it with the agent, and you guide it as it updates the index, entity pages, and log. This human-in-the-loop approach is undoubtedly best practice; it ensures that every claim added to your knowledge graph is verified, contextualized, and truly understood by the human who owns it.

However, in the hyper-dynamic landscape of AI research and cybersecurity, many find themselves in a race against time. If you don’t have the luxury of manual review for every incoming paper or advisory — but still want to bootstrap a high-quality knowledge graph — you need a prototype for autonomous ingestion.

This is what we will cover in this short article, for full details, please subscriber and for codebase see our github repo.


Keep reading with a 7-day free trial
Subscribe to Agentic AI to keep reading this post and get 7 days of free access to the full post archives.

Start trial
A subscription gets you:
Subscriber-only posts and full archive
Post comments and join the community
Yealy subscriber can book 30 minutes virtual meeting with me by sending me an email.
 
Like
Comment
Restack
 
© 2026 ken
University of San Francisco, San Francisco, CA 94104
Unsubscribe

Start writing



Compose:
New Message
MinimizePop-outClose


You have one new message. 

Skip to content
Using Gmail with screen readers
2 of 3,647
MLOps and LLMOps Case Studies
Inbox

Daily Dose of DS <avi@dailydoseofds.com> Unsubscribe
9:25 PM (1 hour ago)
to me

​Master Full-stack AI Engineering​


In today's newsletter:
MLOps and LLMOps case studies.
​The anatomy of a Claude prompt.
Euclidean distance vs. Mahalanobis distance!
TODAY'S ISSUE

production ML
MLOps and LLMOps case studies
With 32 chapters across the MLOps and LLMOps course, we have covered everything from fundamentals to fine-tuning to inference optimization to serving.

We have our final chapter now, and it is one of the most valuable ones.

​Read the final chapter of the MLOps/LLMOps course here →​

​MLOps/LLMOps case studies

This chapter is different from the rest. It shows you how companies like Booking.com, Uber, Stripe, Doordash, and many across big tech, fintech, banking, and e-commerce actually think about ML and AI systems in production.

These are real case studies with real constraints, real failures, and the decisions that shaped how these systems were built.

One example: Booking.com deployed 150+ production models and found that improving model accuracy often did not improve business outcomes at all.

The reasons why are worth understanding deeply to better approach ML projects.

​Read the final chapter of the MLOps/LLMOps course here →​

Why care?
When an ML system breaks in production, it is rarely due to the model architecture. Instead, it’s a silent distribution shift, stale embeddings in the feature store, label leakage the eval pipeline did not catch, or KV caches sized for 512 tokens when production prompts routinely hit 4,000+.


The interesting engineering lives in these operational layers when building reproducible pipelines, data versioning, CI/CD for model deployment, drift monitoring with Evidently and Prometheus, context engineering for LLMs, inference optimization via PagedAttention and continuous batching, serving topology decisions that directly shape cost and latency at scale.

MLOps and LLMOps are the disciplines that bring structure to all of this.

They take the entire surface area around a model, from how training data is tracked and validated, to how inference is optimized and served, to how evaluation catches regressions before users do, and turn it into something repeatable, observable, and maintainable.

The MLOps course (18 parts) covers the full lifecycle of traditional ML in production: reproducibility and versioning with W&B, data and pipeline engineering including sampling, feature stores, and distributed processing, model development and optimization through hyperparameter tuning, pruning, compression, and quantization, deployment via containerization, Kubernetes, AWS, and EKS, monitoring and observability with Evidently, Prometheus, and Grafana, and CI/CD workflows.


The LLMOps course (14 parts) transitions to the new set of challenges that come with foundation models: tokenization, embeddings, and attention internals, context engineering and prompt management, evaluation of open-ended generations including multi-turn and tool use, fine-tuning with LoRA, QLoRA, RLHF, DPO, and GRPO, inference optimization covering KV caching, PagedAttention, FlashAttention, and speculative decoding, and LLM serving concepts including self-hosted vs. API-based access and deployment topology.

You can start reading them here:

​MLOps course (18 parts)​
​LLMOps course (14 parts)​
Thanks for reading!

Claude
​The anatomy of a Claude prompt​
The difference between a mediocre Claude output and a great one almost always comes down to how you structure your prompt. This involves a clear, repeatable structure that gives Claude exactly what it needs to do the job well.

Here's how a well-built Claude prompt breaks down into 8 building blocks, each doing one job:


1) Role
Tell Claude who it is before telling it what to do.

"You are a [ROLE] with expertise in [DOMAIN]. Your tone should be [TONE]. Your audience is [AUDIENCE]."

Setting a role in the system prompt changes how Claude reasons, what it prioritizes, and how it communicates. A "senior backend engineer" writes differently than a "technical copywriter," and Claude picks up on that distinction immediately.

2) Task
State what you want and what success looks like, in the same breath.

"I need you to [SPECIFIC TASK] so that [SUCCESS CRITERIA]."

The "so that" part is what people skip, and it's the part that matters. It gives Claude a way to evaluate its own output. Without it, Claude is guessing what "good" means.

Be direct, skip the preamble, and cut the fluff.

3) Context
This is where you feed Claude everything it needs to do the job well.

Wrap it in XML tags like <context> and </context>, then paste your documents, data, or background inside.

One thing that dramatically improves quality: put long documents at the top of your prompt and your actual query at the end. Anthropic's own testing shows this can improve response quality by up to 30%, especially with complex, multi-document inputs.

4) Examples
Nothing steers output quality like showing Claude what "good" looks like.

Provide 3-5 input/output pairs. Cover normal cases AND edge cases. Wrap them in <examples> tags so Claude doesn't confuse them with instructions.

Claude pays extremely close attention to examples. If your example has a quirk you didn't intend, Claude will replicate it. So make sure every example models the behavior you actually want.

5) Thinking
For anything requiring reasoning, analysis, or multi-step logic, ask Claude to think before answering.

"Before answering, think through this step by step. Use <thinking> tags for your reasoning. Put only your final answer in <answer> tags."

This separates the messy reasoning from the clean output. You get to see how Claude arrived at its answer without that reasoning cluttering the final result.

6) Constraints
Every good prompt has guardrails.

"Never [thing to avoid]. Always [thing to ensure]. If you are about to break a rule, stop and tell me."

That last line is underrated. It turns Claude into a collaborator instead of a blind executor. Instead of silently violating a constraint, Claude flags the conflict and lets you decide.

7) Output Format
Don't leave the format to chance.

"Return your response as [JSON / markdown / table / prose]. Use this exact structure: [structure template]."

If you want JSON, show the exact schema. If you want markdown, show the heading structure. If you want a table, define the columns. The more specific you are about shape, the less time you spend reformatting afterward.

8) Prefill
This one is API-specific, but incredibly powerful.

You can pre-fill the start of Claude's response to skip preamble and lock in the format. Claude will continue from exactly where you left off. No "Sure, I'd be happy to help!" opening, no throat-clearing, just clean output from the first token.

Here's the thing people get wrong about prompting: they think it's about finding the right words. It's actually about giving Claude the right structure.

If you want to go deeper, we wrote a detailed article covering the anatomy of the .claude/ folder, a complete guide to CLAUDE(.)md, hooks, skills, agents, and permissions, and how to set them all up properly.

​You can read it here →​

data science
​Euclidean Distance vs. Mahalanobis Distance!​
Consider the three points below in a dummy dataset with correlated features:


According to Euclidean distance, P1 is equidistant from P2 and P3.

But if we look at the data distribution, something tells us that P2 should be considered closer to P1 than P3 since P2 lies more within the data distribution.


Yet, Euclidean distance can not capture this.

Mahalanobis distance addresses this issue.

It is a distance metric that considers the data distribution during distance computation.

Referring to the above dataset again, with Mahalanobis distance, P2 comes out to be closer to P1 than P3:


How does it work?
The core idea is similar to what we do in ​Principal Component Analysis (PCA)​.

More specifically, we construct a new coordinate system with independent and orthogonal axes. The steps are:

Step 1: Transform the columns into uncorrelated variables.
Step 2: Scale the new variables to make their variance equal to 1.
Step 3: Find the Euclidean distance in this new coordinate system.
So, eventually, we do use Euclidean distance, but in a coordinate system with independent axes.

Uses
One of the most common use cases of Mahalanobis distance is outlier detection.

For instance, in this dataset, P3 is an outlier but Euclidean distance will not capture this.


But Mahalanobis distance provides a better picture:


Moreover, there is a variant of kNN that is implemented with Mahalanobis distance instead of Euclidean distance.

Further reading:

​​We covered 8 more pitfalls in data science projects here →​​
​​This mathematical discussion on the curse of dimensionality will help you understand why Euclidean produces misleading results in high dimensions.
👉 Over to you: What are some other limitations of Euclidean distance?

THAT'S A WRAP

NO-FLUFF RESOURCES TO...
​Succeed in AI Engineering roles​

All businesses care about impact. That’s it!

Can you reduce costs?
Drive revenue?
Can you scale ML models?
Predict trends before they happen?
We have discussed several other topics (with implementations) in the past that align with such topics.

Master full-stack AI engineering
Here are some of them:


Learn MLOps from first principles to production in this course with 18 parts →​
Learn everything about MCPs in this course with 9 parts →​
Learn how to build Agentic systems in this course with 14 parts.
Learn how to build real-world RAG apps, evaluate, and scale them in this course.
Learn sophisticated graph architectures and how to train them on graph data in this course.
So many real-world NLP systems rely on pairwise context scoring. Learn scalable approaches here.
Learn how to run large models on small devices using Quantization techniques.
Learn how to generate prediction intervals or sets with strong statistical guarantees for increasing trust using Conformal Predictions.
Learn how to identify causal relationships and answer business questions using causal inference in this course.
Learn how to scale and implement ML model training in this practical guide.
Learn techniques to reliably test new models in production.
Learn how to build privacy-first ML systems using Federated Learning.
Learn 6 techniques with implementation to compress ML models.
Master full-stack AI engineering
All these resources will help you cultivate key skills that businesses and companies care about the most.

​
Partner with US
ADVERTISE TO 900k+ AI Professionals
Our newsletter puts your products and services directly in front of an audience that matters, including thousands of leaders, senior data scientists, machine learning engineers, data analysts, etc., around the world.

Get in touch today by replying to this email.

Today’s email was brought to you by Avi Chawla and Akshay Pachaar.

​Update your profile | Unsubscribe​

Looking for more? Unlock our premium DS/ML resources.

​

© 2026 Daily Dose of Data Science



Compose:
New Message
MinimizePop-outClose
Skip to main content
Daily Dose of Data Science
Newsletter
Guidebooks
Courses

Sign In
Get Started
MLOps/LLMOps Course
MLOps
Background and Foundations for ML in Production
The Machine Learning System Lifecycle
Reproducibility and Versioning in ML Systems: Fundamentals of Repeatable and Traceable Setups
Reproducibility and Versioning in ML Systems: Weights and Biases for Reproducible ML
Data and Pipeline Engineering: Data Sources, Formats, and ETL Foundations
Data and Pipeline Engineering: Sampling, Data Leakage, and Feature Stores
Data and Pipeline Engineering: Distributed Processing and Workflow Orchestration
Model Development and Optimization: Fundamentals of Development and Hyperparameter Tuning
Model Development and Optimization: Fine-Tuning, Pruning, and Efficiency
Model Development and Optimization: Compression and Portability
Model Deployment: Serialization, Containerization and API for Inference
Model Deployment: Kubernetes
Model Deployment: Cloud Fundamentals
Model Deployment: Introduction to AWS
Model Deployment: EKS Lifecycle and Model Serving
Monitoring and Observability: Core Fundamentals
Monitoring and Observability: Practical Tooling with Evidently, Prometheus, and Grafana
CI/CD Workflows
LLMOps
Foundations of AI Engineering and LLMs
Building Blocks of LLMs: Tokenization and Embeddings
Building Blocks of LLMs: Attention, Architectural Designs and Training
Building Blocks of LLMs: Decoding, Generation Parameters, and the LLM Application Lifecycle
Context Engineering: Foundations, Categories, and Techniques of Prompt Engineering
Context Engineering: Prompt Management, Defense, and Control
Context Engineering: An Introduction to the Information Environment for LLMs
Context Engineering: Memory and Temporal Context
Evaluation: Fundamentals
Evaluation: Model Benchmarks and LLM Application Assessment
Evaluation: Multi-turn Conversations, Tool Use, Tracing, and Red Teaming
LLM Fine-tuning: Techniques for Adapting Language Models
LLM Inference and Optimization: Fundamentals, Bottlenecks, and Techniques
Concepts of LLM Serving
Miscellaneous
MLOps and LLMOps: Case Studies
MLOps/LLMOps Course
33/33
 
22 min read
MLOps and LLMOps: Case Studies
An exploration of real-world MLOps and LLMOps case studies, examining the importance of reliable ML and AI engineering and their significance for business outcomes.

👉
Hey! This is a member-only post. But it looks like you are from Nigeria 🇳🇬. Join today by visiting this membership page for relief pricing of 50% off on your full access, FOREVER.
Introduction
Several AI/ML systems do not just fail because the model is not good enough. They fail because everything around the model was not built to last.


Consider a scenario: A team trains a model, it performs well in tests, and it is deployed to production. Yet conversion rates remain flat. A question from the finance team cannot be answered. Engineers spend weeks investigating why a recommendation system with 94% accuracy is making the product no better. This is not an edge case, rather a reflection of how real-world systems behave.


The companies that eventually get this right, do so by learning lessons that do not always have much to do with algorithms. Their progress comes from how they design systems, handle constraints, and adapt to failure.

This article is the final piece in our MLOps/LLMOps course. Here, we take a look at concrete, real-world examples. We examine a set of carefully chosen case studies drawn from real systems. Each case study focuses on the decisions that shaped the system, why specific approaches were chosen and the constraints teams operated under.

The examples span big tech, fintech, banking, e-commerce, etc. offering a grounded view of how modern AI/ML systems are actually built and sustained.

👉
We have no affiliation, partnership, or association (in any capacity) with any of the companies referenced in these case studies. All trademarks and logos remain the property of their respective owners and are used solely for identification and educational purposes.
#1) The fundamental misunderstanding
Booking.com: Model performance ≠ Business performance
In 2019, Booking.com published a paper at KDD that has changed how most companies today think about ML.

Booking.com: Global News logo
It described 150 deployed production models and one uncomfortable lesson: improving a model's accuracy often did not improve the business metric it was supposed to affect.

There were several reasons for this:

Value saturation: the model had already captured most of the available gain, and further accuracy improvements had nothing much left to unlock.
Segment saturation: when testing a new model against the current one, the two models increasingly agree on what to show users, shrinking the population actually exposed to any difference. The testable segment becomes too small to move aggregate metrics.
Proxy metric over-optimization: the model had learned to maximize something measurable that was only loosely correlated with what the business actually cared about.
👉
This means the model gets better at predicting the label it was trained on, but that label is an imperfect proxy for the business outcome.
Uncanny valley effect: as a model becomes too accurate (predicting user behavior so precisely that it feels like the system knows too much), it can unsettle users, producing a negative effect on business value.
Their solution was to treat randomized controlled trials (RCTs) as mandatory infrastructure, not optional validation.

👉
A randomized controlled trial (RCT) is a type of scientific experiment designed to evaluate the efficacy of an intervention by minimizing bias through the random allocation of participants to one or more comparison groups.
This means every single model gets validated through an RCT before it stays in production. This was not a qualitative review or a conversation about the AUC, but rather an actual experiment measuring whether users behaved differently in a way that matters to the business.

The deeper insight was about how teams construct problems. Switching a preferences model from click data to natural language processing on guest reviews produced more business value than any model-level improvement had. The framing of the problem and project scoping mattered more than the sophistication of the solution.


 
 
 
This lesson is for paying subscribers only
Unlock Full Access
Already have an account? Sign in

Published on Apr 6, 2026
Share
Previous — LLMOps
Concepts of LLM Serving
On this page

Introduction
#1) The fundamental misunderstanding
Booking.com: Model performance ≠ Business performance
Daily Dose of Data Science
A daily column with insights, observations, tutorials and best practices on python and data science. Read by industry professionals at big tech, startups, and engineering students.
Menu
Contact
FAQ
Daily Dose of Data Science © 2026


None selected

Skip to content
Using Gmail with screen readers
is:important 
21 of 3,660
Keparthy
Inbox

Adedoyinsola Ogungbesan <jdmasciano2@gmail.com>
Thu, Apr 2, 10:42 PM (3 days ago)
to me

LLM Knowledge Bases

Something I'm finding very useful recently: using LLMs to build personal knowledge bases for various topics of research interest. In this way, a large fraction of my recent token throughput is going less into manipulating code, and more into manipulating knowledge (stored as markdown and images). The latest LLMs are quite good at it. So:

Data ingest:
I index source documents (articles, papers, repos, datasets, images, etc.) into a raw/ directory, then I use an LLM to incrementally "compile" a wiki, which is just a collection of .md files in a directory structure. The wiki includes summaries of all the data in raw/, backlinks, and then it categorizes data into concepts, writes articles for them, and links them all. To convert web articles into .md files I like to use the Obsidian Web Clipper extension, and then I also use a hotkey to download all the related images to local so that my LLM can easily reference them.

IDE:
I use Obsidian as the IDE "frontend" where I can view the raw data, the the compiled wiki, and the derived visualizations. Important to note that the LLM writes and maintains all of the data of the wiki, I rarely touch it directly. I've played with a few Obsidian plugins to render and view data in other ways (e.g. Marp for slides).

Q&A:
Where things get interesting is that once your wiki is big enough (e.g. mine on some recent research is ~100 articles and ~400K words), you can ask your LLM agent all kinds of complex questions against the wiki, and it will go off, research the answers, etc. I thought I had to reach for fancy RAG, but the LLM has been pretty good about auto-maintaining index files and brief summaries of all the documents and it reads all the important related data fairly easily at this ~small scale.

Output:
Instead of getting answers in text/terminal, I like to have it render markdown files for me, or slide shows (Marp format), or matplotlib images, all of which I then view again in Obsidian. You can imagine many other visual output formats depending on the query. Often, I end up "filing" the outputs back into the wiki to enhance it for further queries. So my own explorations and queries always "add up" in the knowledge base.

Linting:
I've run some LLM "health checks" over the wiki to e.g. find inconsistent data, impute missing data (with web searchers), find interesting connections for new article candidates, etc., to incrementally clean up the wiki and enhance its overall data integrity. The LLMs are quite good at suggesting further questions to ask and look into.

Extra tools:
I find myself developing additional tools to process the data, e.g. I vibe coded a small and naive search engine over the wiki, which I both use directly (in a web ui), but more often I want to hand it off to an LLM via CLI as a tool for larger queries.

Further explorations:
As the repo grows, the natural desire is to also think about synthetic data generation + finetuning to have your LLM "know" the data in its weights instead of just context windows.

TLDR: raw data from a given number of sources is collected, then compiled by an LLM into a .md wiki, then operated on by various CLIs by the LLM to do Q&A and to incrementally enhance the wiki, and all of it viewable in Obsidian. You rarely ever write or edit the wiki manually, it's the domain of the LLM. I think there is room here for an incredible new product instead of a hacky collection of scripts. 

Compose:
New Message
MinimizePop-outClose




Below is the transcript of the video followed by Mermaid diagrams illustrating the concepts discussed.

### Video Transcript: Building Trust and Security in Agentic AI Systems

**Grant Miller (Distinguished Engineer, IBM):**
Howdy everyone. In this video, we will look at how to ensure secure and reliable AI interactions and discuss how trust is established and maintained across agentic AI systems. As part of establishing trust, the concept of verifiable agent identities is also explored.

Building trust and security for IT systems has long been part of what we do. The first real standards actually emerged back in 1985 around security. And while AI systems are like those in many ways, there are unique challenges that bring new risk, especially when we consider the non-deterministic behavior of AI interactions.

All right, let's start by drawing a typical AI or agentic flow. We start with a **user**, and that user interacts with a **chat**. That chat then determines what the user's going to do and goes to an **orchestrator**. And that orchestrator determines, okay, how is this flow ultimately going to look? So we may have a couple of **AI agents** (A1, A2). We could have one, we could have multiple of these. The orchestrator creates a flow to interact. 

And then ultimately, we're going to have some **tool** that we want to connect to, whether that's data or systems. And now we see an emergence of **MCP servers** that the agents talk to, and then that ultimately talks into the tool. All right, so that's our first flow. 

Now, also in agentic systems, we have **LLMs**. And these LLMs can help us in a variety of places. They may work with the chat, they may work with the orchestrator to give some intelligence to developing the flow, they may work with each of the individual agents as we determine what they need to do and how they're going to respond to a prompt from the original user.

The other thing that we see a lot of is we have a company's **identity provider (IdP)** that's basically authenticating the user. We authenticate the user at the very beginning, and that results in a **token** that we then can propagate through the whole flow down to the tool. And that says who the user is, so we know what kinds of things at the tool the user is allowed to do. So this is a typical agentic flow.

So let's start thinking about then, all right, what are some of the things that where there's risk and where there's errors that we need to take into consideration? Well, the first thing that we really want to think about is a **credential replay**. And what this basically says is that there is some other person that wants to take over the identity of who we think is using the system, gain their privileges and their accesses, and then use that token in a bad way to propagate through and get access to things that we don't want them to get access to. 

Now, so how can this happen when we have a particular flow? Well, there's several ways that this can happen. One of the ways is that in our development of our agentic system, we may actually in any of these steps send up our token that was authenticated here into the LLM as part of just the communication with the LLM. And what happens is now it's embedded in the LLM, and a bad actor can actually use prompt engineering to get the LLM to give up that token, get access to that token or the credentials, and then use that along the process. 

The other thing that can happen is we can have a **man-in-the-middle (MITM)** attack where somewhere along this path there's somebody that's inserted themselves because we have a non-secure flow or non-secure stores, and they can actually intercept these tokens, get a hold of them, and then use them to replay again and get access to things that we don't want them to get access to. 

So in this part of this, how do we prevent these kinds of risks from happening? Well, first thing when we're talking about man-in-the-middle is we can use **TLS or mTLS** along our whole communication flow so that's encrypted and secured and we can prevent someone getting in the middle. If we store credentials, if we store anything along this flow, encrypt those where they're stored so we can do a lot to kind of prevent the man-in-the-middle. The other thing is just make sure you're not passing in identity information to the LLM. The LLM doesn't need that; it just needs to be able to organize and figure out what the task is for it. So do not send that in.

The next thing that we have to look at if we talk about securing our flows and being able to trust our agentic system is we need to look at **rogue agents**. So we have agents that are somewhere pop up and they're either communicating with some of these other agents, they're communicating with MCP, and what they're doing is they're **spoofing the identity** of these other agents. So they're saying, "Hey, I'm the real agent, talk to me and get me access to this tool." And we don't want this to happen. We want to make sure that we can trust that we know who the legitimate agents are. 

And to do that, we really start looking at, again, we take an identity provider and we start using this for agents. So we want to know the **identity of the agents** and we want to be able to **authenticate the agents**. So we have an agent come up, we have an agent come up, and we say, "Please prove you are who you say that you are." This prevents us, much like we would do with a bad actor, then a rogue agent isn't able to authenticate itself and we can trust exactly who these agents are and we know whether or not it's a rogue agent or not. And when we get to an MCP server at this point, then we can **validate**. In fact, we can actually validate it at multiple points throughout this flow. When Agent 1 is talking to Agent 2, we can go up and validate that we trust that that was an authenticated legitimate agent. Same with the MCP; we can look at Agent 2 and make sure that we trust that it was authenticated. So this is a big piece of making sure that we know who the agents are in this system. 

Now, next piece that we want to look at is **impersonation**. And what this is really saying is that even if we kind of think that we trust who an agent is, we don't want them to tell us, "Well, this is the person that I am working for," without having any validation of that individual. So in other words, the agent is impersonating the user. And so what we do here is we actually start looking at **delegation**. And this really is about having an agent work on behalf of a user. So what we want to do is make sure that we have this user properly authenticated, we take their token, and that becomes part of—once an agent authenticates itself—now we have a combined token that has the **subject (the user)** and has the **actor (the agent)**. So now when we're going through the flow, we can trust that we've authenticated the user because that's contained within our token and we can also trust that we have authenticated the agent and who they're supposed to be operating on behalf of. And all of this happens at the identity provider. Not anywhere along this way can an agent assert what it's doing; it has to be validated and provided by an independent party, in this case, which is the identity provider. So this is another piece of this. 

Now, as we talked about at the very beginning, we have these tokens that kind of flow through the system. That is also a point of risk because we just need to make sure that at each node and each hop, that token is actually the one that we trust through the entire flow. We do that through doing a **token exchange**. And what this really says is that at each node and hop, we make a call to our provider and we say, "Please exchange the incoming token for another." We know the starting point, we know the endpoint, we bring those tokens in, then we exchange it. So the trust and the validation is really for this flow, then we trust and validate for this flow. So that way, we know that everything is propagating correctly along this flow. Again, so we trust the user, trust the agents, securely move the identities through the system as we're getting it to the tools. 

The next thing that we really want to think about then is at the tool side is **over-permissioning**. And what this says is that a user could be allowed to do a lot of stuff, an agent could be allowed to do a lot of stuff, but we only want what happens within this flow to only be what is needed for the prompt that's happening and what is the actual tool that we need to connect to. A user may be able to connect to lots of tools, but in the context of this flow, we only want to be able to show what that user can connect to, same with the agents. 

And this really gets then into **scopes**. When we do these exchanges at each node of this flow, we're validating everything, but we're also restricting the scopes in the token to only be what is necessary. Agent 1 can talk to Agent 2; it has an audience of Agent 2. Agent 2 can connect with this tool; so we go through MCP and we validate all this. So this really then gets us a good end-to-end flow that we can now trust. 

Now, the final piece that we want to think about when we're looking at how do we trust and secure our agentic system is really the **last mile**. And this is really happening between MCP and the tool. From this point, it's tokens, it's flowing, we are trusting, we are validating. But now the MCP server is going to talk to a tool, and it may do that over an API, it may do that over a variety of different mechanisms which really are not necessarily what we've established in the flow. So how do we do that? We don't want the MCP server to store and keep credentials that it uses to access the tool because now we have a potential risk and exposure here. So what we do for the last mile is we introduce a **vault**, a secure vault. And this manages the credentials to the tool and then feeds a **temporary credential** to MCP. So we have the user, we have the agent, it wants to connect to a tool, it does an exchange within a vault to get a temporary credential that is used for the tool, and now we connect to the tool. 

All right, so this is a good view of how we can start through a typical agentic system and do things with **trust**, where we trust the identities and we trust the authentication, so we know who is operating across this flow and we trust that. We also can make sure that we're doing **secure flows**, and this is really about **authorization**, which ultimately is our scopes and what we're allowing and using least privilege. It is also about **delegation**, making sure that the agents, we know who they are and they're working on behalf of a user and we can trust those two components. And then it's about **propagation**—can all this information be securely transferred along our agentic flow and back to the results of the prompt? And doing these things will allow you to have trust in that agentic system.

---

### Mermaid Diagrams

#### 1. Typical Agentic AI Flow
This diagram illustrates the logical flow of a user request through an agentic system, including the supporting infrastructure like LLMs and Identity Providers.

```mermaid
graph LR
    subgraph UserInteraction
    User((User)) -- Prompt --> Chat[Chat Interface]
    end

    subgraph CoreFlow
    Chat -- Request --> Orch[Orchestrator]
    Orch -- Plan --> A1[Agent 1]
    A1 -- Task --> A2[Agent 2]
    A2 -- Operation --> MCP[MCP Server]
    MCP -- Command --> Tool[(System/Data Tool)]
    end

    subgraph Intelligence
    LLM(LLM Services) -. Intelligence .-> Chat
    LLM -. Flow logic .-> Orch
    LLM -. Agent logic .-> A1
    LLM -. Agent logic .-> A2
    end

    subgraph Security_Identity
    IdP[Identity Provider] -- Auth Token --> User
    IdP -. Propagation .-> Orch
    IdP -. Propagation .-> A1
    IdP -. Propagation .-> A2
    end
```

#### 2. Risks vs. Security Solutions
This diagram highlights the specific threats mentioned in the video and the corresponding architectural solutions used to mitigate them.

```mermaid
graph TD
    subgraph Threats
    R1[Credential Replay]
    R2[Man-in-the-Middle]
    R3[Identity Spoofing/Rogue Agents]
    R4[Impersonation]
    R5[Over-Permissioning]
    end

    subgraph Solutions
    S1[TLS / mTLS Encryption]
    S2[Agent Authentication]
    S3[Delegation & Combined Tokens]
    S4[Token Exchange per Hop]
    S5[Scoped Tokens / Least Privilege]
    S6[Secure Credential Vault]
    end

    R1 -.-> S4
    R1 -.-> S3
    R2 -.-> S1
    R3 -.-> S2
    R4 -.-> S3
    R5 -.-> S5
    R5 -.-> S6
```

#### 3. The Secure Token & Last Mile Architecture
This diagram focuses on the "trust chain" — how identities are combined and how the final connection to the tool is secured using a vault.

```mermaid
sequenceDiagram
    participant User
    participant IdP as Identity Provider
    participant Agent
    participant Vault as Secure Vault
    participant Tool

    User->>IdP: Authenticate User
    IdP-->>User: User Token (Subject)
    
    User->>Agent: Request + User Token
    
    Agent->>IdP: Authenticate Agent
    IdP-->>Agent: Agent Identity (Actor)
    
    Note over Agent,IdP: Token Exchange & Delegation
    Agent->>IdP: Exchange for Combined Token
    IdP-->>Agent: Delegation Token (Subject + Actor + Scopes)
    
    Note over Agent,Tool: The Last Mile
    Agent->>Vault: Present Scoped Token
    Vault->>Vault: Validate Identity & Scope
    Vault-->>Agent: Temporary Tool Credential
    
    Agent->>Tool: Execute with Temp Credential
    Tool-->>Agent: Result
```