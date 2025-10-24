'use client';

import { useState, useEffect } from 'react';

const slides = [
  {
    id: 1,
    content: (
      <div className="slide-content text-center">
        <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-gray-800 mb-8 leading-tight">Building Reliable AI Research Assistants: A Durable Execution Approach</h1>
        <p className="text-2xl md:text-3xl lg:text-4xl" style={{color: '#00549f'}}>Orchestrating Multi-Agent Systems for Academic Literature Review</p>
        <p className="text-xl md:text-2xl text-gray-600 mt-8">RWTH Aachen University - Chair of Databases and Information Systems (i5)</p>
        <p className="text-base md:text-lg text-gray-500 mt-4">Presenter: Jin, Er | jin@dbis.rwth-aachen.de</p>
      </div>
    )
  },
  {
    id: 2,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">Research Motivation: The PhD Student Challenge</h2>
        <div className="space-y-8">
          <div className="p-6 rounded-lg border-l-4 bg-blue-50 border-blue-400">
            <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-blue-900">The Problem</h3>
            <ul className="space-y-4 text-lg md:text-xl">
              <li className="flex items-start">
                <span className="mr-3 text-blue-600">•</span>
                <span>Reading and validating <strong>200+ papers</strong> is normal during PhD research</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 text-blue-600">•</span>
                <span>Reviewing and studying <strong>10+ papers per week</strong> can cost significant time</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 text-blue-600">•</span>
                <span>More than <strong>10+ hours per week</strong> on literature review is very common</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 text-blue-600">•</span>
                <span>Information overload and synthesis difficulty</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 text-blue-600">•</span>
                <span>Critical bottleneck in research progress</span>
              </li>
            </ul>
          </div>
          <div className="p-6 rounded-lg border-l-4 bg-amber-50 border-amber-400">
            <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-gray-800">The Explosion Challenge</h3>
            <ul className="space-y-3 text-lg md:text-xl">
              <li className="flex items-start">
                <span className="mr-3 text-amber-600">•</span>
                <span>NeurIPS submissions grew <strong>85% in 4 years</strong> (9,467 in 2020 → 17,491 in 2024)<sup style={{color: '#00549f'}}>46</sup></span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 text-amber-600">•</span>
                <span>Top-tier AI conferences published <strong>87,137 papers</strong> from 2014-2023<sup style={{color: '#00549f'}}>47</sup></span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 text-amber-600">•</span>
                <span>Tracking latest trends becomes increasingly difficult with rapid publication growth</span>
              </li>
            </ul>
          </div>
          <div className="p-6 bg-gray-50 rounded-lg border-2 border-gray-200">
            <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-gray-800">Research Question</h3>
            <p className="text-xl md:text-2xl italic" style={{color: '#00549f'}}>"Can AI agents reliably automate academic literature review while maintaining scientific rigor?"</p>
          </div>
          <p className="text-base text-gray-500 mt-4">Related work on literature review methods and publication trends<sup style={{color: '#00549f'}}>15,43,46,47</sup></p>
        </div>
      </div>
    )
  },
  {
    id: 3,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-10 text-gray-800">Current Solutions & Their Limitations</h2>
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="p-4 rounded-lg font-bold text-xl md:text-2xl text-center bg-blue-100 text-blue-900">Approach</div>
            <div className="p-4 rounded-lg font-bold text-xl md:text-2xl text-center bg-blue-100 text-blue-900">Description</div>
            <div className="p-4 rounded-lg font-bold text-xl md:text-2xl text-center bg-blue-100 text-blue-900">Limitations</div>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-white p-5 rounded-lg border-2 border-gray-200">
            <div className="font-bold text-xl md:text-2xl text-gray-800">Manual Review</div>
            <div className="text-lg md:text-xl">PhD student reads each paper</div>
            <div className="text-lg md:text-xl text-red-600 font-semibold">Slow (weeks), not scalable</div>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-gray-50 p-5 rounded-lg border-2 border-gray-200">
            <div className="font-bold text-xl md:text-2xl text-gray-800">Search Tools</div>
            <div className="text-lg md:text-xl">Google Scholar, Semantic Scholar</div>
            <div className="text-lg md:text-xl text-red-600 font-semibold">No analysis, just retrieval</div>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-white p-5 rounded-lg border-2 border-gray-200">
            <div className="font-bold text-xl md:text-2xl text-gray-800">Reference Managers</div>
            <div className="text-lg md:text-xl">Zotero, Mendeley, EndNote</div>
            <div className="text-lg md:text-xl text-red-600 font-semibold">Organization only, no synthesis</div>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-gray-50 p-5 rounded-lg border-2 border-gray-200">
            <div className="font-bold text-xl md:text-2xl text-gray-800">LLM-Based Agents</div>
            <div className="text-lg md:text-xl">ChatGPT, Claude for summaries</div>
            <div className="text-lg md:text-xl text-red-600 font-semibold">Unreliable, hallucinations</div>
          </div>

          <div className="p-8 bg-amber-50 rounded-lg border-l-4 border-amber-500 mt-8">
            <p className="text-xl md:text-2xl text-gray-800"><strong>Research Gap:</strong> No production-ready intelligent research assistant that is both capable AND reliable.</p>
          </div>
          <p className="text-lg text-gray-500 mt-4">Survey of current tools and LLM agents<sup style={{color: '#00549f'}}>1,2,10</sup></p>
        </div>
      </div>
    )
  },
  {
    id: 4,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">Why Agentic AI? Everyone Is Moving</h2>

        <div className="grid md:grid-cols-3 gap-8 mb-8">
          {/* Tech Giants Column */}
          <div className="p-6 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <h3 className="text-2xl md:text-3xl font-bold mb-4 text-blue-900">Tech Giants</h3>
            <ul className="space-y-3 text-lg md:text-xl">
              <li><strong>Anthropic</strong> - Coding agents (Claude Code)<sup style={{color: '#00549f'}}>48</sup></li>
              <li><strong>OpenAI</strong> - Deep Research agent</li>
              <li><strong>Microsoft</strong> - Copilot agents (Sales, HR, Finance)</li>
            </ul>
          </div>

          {/* Image Column */}
          <div className="flex items-center justify-center">
            <img src="/presentation/memix-long-queue-no-queue.jpeg" alt="AI Agents vs Rule-Based Workflows" className="w-full rounded-lg shadow-lg" />
          </div>

          {/* Startups Column */}
          <div className="p-6 bg-green-50 rounded-lg border-l-4 border-green-500">
            <h3 className="text-2xl md:text-3xl font-bold mb-4 text-green-900">Startups</h3>
            <ul className="space-y-3 text-lg md:text-xl">
              <li><strong>n8n</strong> - $1B+ valuation<sup className="text-green-600">49</sup></li>
              <li><strong>Manus AI</strong> - $500M valuation<sup className="text-green-600">50</sup></li>
              <li><strong>Dify</strong> - Open-source platform</li>
              <li><strong>Zapier</strong> - 8,000+ apps</li>
            </ul>
          </div>
        </div>

        {/* Key Stat */}
        <div className="p-6 rounded-lg border-2 mb-6 bg-amber-50 border-amber-400">
          <p className="text-xl md:text-2xl text-center text-gray-800">
            "2025: The Year of AI Agents"<sup style={{color: '#00549f'}}>51</sup> — 33% of enterprise software will have agentic AI by 2028
          </p>
        </div>

        {/* Bottom Banner */}
        <div className="p-5 bg-gray-50 rounded-lg border-l-4 border-gray-400">
          <p className="text-xl md:text-2xl font-semibold text-gray-800 text-center">But does popularity = production reliability?</p>
        </div>
      </div>
    )
  },
  {
    id: 5,
    content: (
      <div className="slide-content">
        <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gray-800">AI Agents: Promise vs. Reality</h2>
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div className="p-5 bg-green-50 rounded-lg border-l-4 border-green-600">
            <h3 className="text-xl md:text-2xl font-semibold mb-3 text-gray-800">The Promise</h3>
            <ul className="space-y-2 text-base text-gray-700">
              <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> Read & summarize papers automatically</li>
              <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> Extract methodologies & compare</li>
              <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> Map citation networks</li>
              <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> Generate review sections</li>
              <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> <strong>Weeks → Days</strong></li>
            </ul>
          </div>
          <div className="p-5 bg-red-50 rounded-lg border-l-4 border-red-400">
            <h3 className="text-xl md:text-2xl font-semibold mb-3 text-gray-800">The Reality: Failure Modes</h3>

            <div className="space-y-3">
              <div className="bg-white p-3 rounded border-l-4 border-gray-400">
                <p className="text-lg font-bold text-gray-800 mb-1">1. State Loss</p>
                <p className="text-base text-gray-700"><strong>Replit Agent:</strong> Deleted production database during code freeze<sup style={{color: '#00549f'}}>53</sup></p>
                <p className="text-sm text-gray-600 italic mt-1">→ 1,200+ companies lost all data</p>
              </div>

              <div className="bg-white p-3 rounded border-l-4 border-gray-400">
                <p className="text-lg font-bold text-gray-800 mb-1">2. Hallucinations</p>
                <p className="text-base text-gray-700"><strong>Air Canada Chatbot:</strong> Invented fake bereavement policy<sup style={{color: '#00549f'}}>54</sup></p>
                <p className="text-sm text-gray-600 italic mt-1">→ Company held liable in court (Moffatt v. Air Canada)</p>
              </div>

              <div className="bg-white p-3 rounded border-l-4 border-gray-400">
                <p className="text-lg font-bold text-gray-800 mb-1">3. High Failure Rate</p>
                <p className="text-base text-gray-700"><strong>Carnegie Mellon "TheAgentCompany":</strong> Simulated company with AI employees<sup style={{color: '#00549f'}}>52</sup></p>
                <p className="text-sm text-gray-600 italic mt-1">→ Tasks: code reviews, data analysis, HR duties. GPT-4o: 91.4% failed</p>
              </div>

              <div className="bg-white p-3 rounded border-l-4 border-gray-400">
                <p className="text-lg font-bold text-gray-800 mb-1">4. Production Viability</p>
                <p className="text-base text-gray-700"><strong>Gartner Prediction:</strong> 40% of agentic AI projects canceled by 2027<sup style={{color: '#00549f'}}>55</sup></p>
                <p className="text-sm text-gray-600 italic mt-1">→ Due to unclear business value & inadequate risk controls</p>
              </div>
            </div>
          </div>
        </div>
        <div className="p-5 bg-white rounded-lg border-2 border-gray-300">
          <p className="text-lg md:text-xl font-semibold text-center text-gray-800">
            💡 Key Insight: This is NOT an AI problem — it's a <strong>systems reliability</strong> problem
          </p>
        </div>
        <p className="text-sm text-gray-500 mt-3">LLM hallucination and agent evaluation research<sup style={{color: '#00549f'}}>9,10,16,22</sup></p>
      </div>
    )
  },
  {
    id: 6,
    content: (
      <div className="slide-content">
        <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-800">How AI Agents Work: The MCP Architecture</h2>
        <p className="text-lg md:text-xl mb-5">Model Context Protocol (MCP): Anthropic's open standard for connecting AI agents to external systems<sup style={{color: '#00549f'}}>56</sup></p>

        {/* Agentic AI = Sophisticated For-Loop */}
        <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-400 mb-5">
          <h3 className="text-xl md:text-2xl font-bold mb-2 text-gray-800">Mental Model: Agentic AI = Sophisticated For-Loop<sup style={{color: '#00549f'}}>3,57</sup></h3>
          <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg overflow-x-auto text-sm md:text-base font-mono">
            <code>
              <span style={{color: '#c678dd'}}>while</span> <span style={{color: '#c678dd'}}>not</span> <span style={{color: '#61afef'}}>task_complete</span>:<br />
              {'    '}<span style={{color: '#61afef'}}>context</span> <span style={{color: '#abb2bf'}}>=</span> <span style={{color: '#61afef'}}>mcp</span>.<span style={{color: '#e5c07b'}}>get_resources</span>(){'      '}<span style={{color: '#5c6370'}}># Read data (Know)</span><br />
              {'    '}<span style={{color: '#61afef'}}>action</span> <span style={{color: '#abb2bf'}}>=</span> <span style={{color: '#61afef'}}>llm</span>.<span style={{color: '#e5c07b'}}>plan</span>(<span style={{color: '#61afef'}}>context</span>, <span style={{color: '#61afef'}}>goal</span>){'   '}<span style={{color: '#5c6370'}}># Decide using Prompts (Guide)</span><br />
              {'    '}<span style={{color: '#61afef'}}>result</span> <span style={{color: '#abb2bf'}}>=</span> <span style={{color: '#61afef'}}>mcp</span>.<span style={{color: '#e5c07b'}}>execute_tool</span>(<span style={{color: '#61afef'}}>action</span>){'  '}<span style={{color: '#5c6370'}}># Execute action (Do)</span><br />
              {'    '}<span style={{color: '#61afef'}}>state</span>.<span style={{color: '#e5c07b'}}>update</span>(<span style={{color: '#61afef'}}>result</span>){'               '}<span style={{color: '#5c6370'}}># Update and loop</span>
            </code>
          </pre>
          <p className="text-base md:text-lg mt-2 text-gray-700 italic">→ Agents continuously loop: <strong>observe → decide → act → update</strong> (ReAct's "think-act-observe" cycle<sup style={{color: '#00549f'}}>3</sup>)</p>
        </div>

        <div className="grid md:grid-cols-2 gap-5 mb-5">
          {/* Architecture */}
          <div className="space-y-3">
            <div className="p-4 bg-gray-50 rounded-lg border-2 border-gray-300">
              <h3 className="text-xl md:text-2xl font-bold mb-3 text-gray-800">MCP Stack</h3>
              <div className="space-y-2 text-base md:text-lg">
                <div className="p-2 bg-white rounded border border-gray-300">
                  <p><strong>MCP Host</strong> (Claude, AI IDE)</p>
                </div>
                <div className="text-center text-xl text-gray-400">↓</div>
                <div className="p-2 bg-white rounded border border-gray-300">
                  <p><strong>MCP Client</strong> (Connection manager)</p>
                </div>
                <div className="text-center text-xl text-gray-400">↓</div>
                <div className="p-2 bg-white rounded border border-gray-300">
                  <p><strong>MCP Server</strong> (APIs, databases, tools)</p>
                </div>
              </div>
            </div>
          </div>

          {/* 3 Essential Elements */}
          <div className="space-y-2">
            <div className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
              <h3 className="text-lg md:text-xl font-bold mb-1 text-blue-900">1. Tools (Do)</h3>
              <p className="text-base md:text-lg">Execute actions in the loop</p>
              <p className="text-sm italic mt-1 text-blue-700">Example: Search arXiv, download PDF</p>
            </div>

            <div className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
              <h3 className="text-lg md:text-xl font-bold mb-1 text-blue-900">2. Resources (Know)</h3>
              <p className="text-base md:text-lg">Data to inform decisions</p>
              <p className="text-sm italic mt-1 text-blue-700">Example: PDF contents, citations</p>
            </div>

            <div className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
              <h3 className="text-lg md:text-xl font-bold mb-1 text-blue-900">3. Prompts (Guide)</h3>
              <p className="text-base md:text-lg">Templates for the loop logic</p>
              <p className="text-sm italic mt-1 text-blue-700">Example: "Analyze this paper for methods"</p>
            </div>
          </div>
        </div>

        {/* Bottom: The Problem */}
        <div className="p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
          <h3 className="text-xl font-bold mb-2 text-red-800">But There's a Problem...</h3>
          <p className="text-base md:text-lg text-red-700">MCP handles <strong>connections</strong>, but NOT <strong>durability</strong>. When agents crash mid-loop, all state is lost — the entire loop must restart.<sup className="text-red-400">52,53</sup></p>
        </div>
      </div>
    )
  },
  {
    id: 7,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">The Agent Reliability Crisis</h2>
        <p className="text-xl md:text-2xl mb-8 text-gray-700">Agents are reasoning models on steroids—powerful, but with dangerous side effects when used without proper architectural supervision.<sup style={{color: '#00549f'}}>18,19</sup></p>

        <div className="p-6 bg-blue-50 rounded-lg border-l-4 border-blue-500 mb-6">
          <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-blue-900">Key Reliability Problems</h3>
          <ul className="space-y-4 text-lg md:text-xl text-blue-800">
            <li>• <strong>State-Loss Catastrophe:</strong> Any crash loses ALL progress—like a patient losing consciousness mid-surgery<sup style={{color: '#00549f'}}>18,19</sup></li>
            <li>• <strong>LLM = Unreliable Microservice:</strong> Network failures + semantic failures (hallucinations, malformed output)<sup style={{color: '#00549f'}}>9,16,22</sup></li>
          </ul>
        </div>

        <div className="p-6 bg-amber-50 rounded-lg border-l-4 border-amber-500 mb-6">
          <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-amber-900">Side Effects Taxonomy</h3>
          <ul className="space-y-3 text-lg md:text-xl text-amber-800">
            <li>• <strong>Execution:</strong> Crashes, state-loss, timeouts</li>
            <li>• <strong>Cognitive:</strong> Hallucinations, flawed logic</li>
            <li>• <strong>Systemic:</strong> Tool failures, coordination issues<sup style={{color: '#00549f'}}>25,31,32</sup></li>
          </ul>
        </div>

        <div className="p-6 bg-red-50 rounded-lg border-l-4 border-red-500">
          <p className="text-lg md:text-xl text-red-800"><strong>Real Example:</strong> Replit agent deleted production database—lost track of state and actions<sup style={{color: '#00549f'}}>53</sup></p>
        </div>
      </div>
    )
  },
  {
    id: 8,
    content: (
      <div className="slide-content">
        <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gray-800">The Solution: Temporal Orchestration</h2>
        <p className="text-lg md:text-xl mb-5">We choose <strong>Temporal</strong> as our orchestration framework—an open-source durable execution platform designed for reliable distributed systems.<sup style={{color: '#00549f'}}>19,28</sup></p>

        <div className="mb-6 p-5 bg-gray-50 rounded-lg border-2 border-gray-300">
          <h3 className="font-bold text-xl md:text-2xl mb-3 text-gray-800">Why Temporal?</h3>
          <div className="grid md:grid-cols-2 gap-2 text-base md:text-lg">
            <div className="flex items-start"><span className="text-green-600 mr-2 text-xl">✓</span><span>Open-source & production-ready</span></div>
            <div className="flex items-start"><span className="text-green-600 mr-2 text-xl">✓</span><span>Easy to deploy (Docker/Cloud)</span></div>
            <div className="flex items-start"><span className="text-green-600 mr-2 text-xl">✓</span><span>Async support & distributed reliability</span></div>
            <div className="flex items-start"><span className="text-green-600 mr-2 text-xl">✓</span><span>Complete audit trail & debugging</span></div>
            <div className="flex items-start"><span className="text-green-600 mr-2 text-xl">✓</span><span>Rich ecosystem (Python, TS, Go SDKs)</span></div>
            <div className="flex items-start"><span className="text-green-600 mr-2 text-xl">✓</span><span>Durable execution guarantees</span></div>
          </div>
        </div>

        <div className="mb-6 p-5 bg-blue-50 rounded-lg border-l-4 border-blue-500">
          <h3 className="font-bold text-xl md:text-2xl mb-2 text-blue-900">The Architecture Philosophy</h3>
          <p className="text-base md:text-lg text-blue-700"><strong>Humans design the workflow structure</strong> (the solid architectural foundation), while <strong>agents/LLMs serve as the brain</strong> deciding which tools to use for each task.<sup style={{color: '#00549f'}}>28,29</sup></p>
        </div>

        <div className="space-y-3">
          <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
            <h3 className="font-bold text-lg md:text-xl text-green-900 mb-1">Deterministic Workflows</h3>
            <p className="text-base md:text-lg text-green-700">Human-designed orchestration logic—the "master plan" that coordinates the process.<sup className="text-green-600">29</sup></p>
          </div>
          <div className="p-4 bg-amber-50 rounded-lg border-l-4 border-amber-500">
            <h3 className="font-bold text-lg md:text-xl text-amber-900 mb-1">Non-Deterministic Activities</h3>
            <p className="text-base md:text-lg text-amber-700">Agent brain decides which tools to execute—LLM calls, API requests, database queries.<sup className="text-amber-600">29</sup></p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg border-l-4 border-purple-500">
            <h3 className="font-bold text-lg md:text-xl text-purple-900 mb-1">Durable State Persistence</h3>
            <p className="text-base md:text-lg text-purple-700">Temporal records every step as immutable events—crashes don't lose progress.<sup className="text-purple-600">19</sup></p>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 9,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">Code Example: A Durable Agent in Practice</h2>
        <p className="text-xl md:text-2xl mb-8">With a durable execution framework, the application code becomes simpler because the platform handles the complexity of state management and retries.</p>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
            <h3 className="font-semibold text-2xl md:text-3xl mb-4 text-green-900">1. Define Tools as Activities</h3>
            <p className="mb-4 text-lg md:text-xl text-green-700">Isolate fallible network calls. Temporal will manage retries.</p>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-base md:text-lg font-mono">
              <code>
                <span style={{color: '#5c6370'}}># activities/tools.py</span><br />
                <span style={{color: '#c678dd'}}>from</span> <span style={{color: '#61afef'}}>temporalio</span> <span style={{color: '#c678dd'}}>import</span> <span style={{color: '#61afef'}}>activity</span><br />
                <br />
                <span style={{color: '#abb2bf'}}>@</span><span style={{color: '#61afef'}}>activity</span>.<span style={{color: '#e5c07b'}}>define</span><br />
                <span style={{color: '#c678dd'}}>async</span> <span style={{color: '#c678dd'}}>def</span> <span style={{color: '#e5c07b'}}>get_weather</span>(<span style={{color: '#61afef'}}>city</span><span style={{color: '#abb2bf'}}>:</span> <span style={{color: '#61afef'}}>str</span>) <span style={{color: '#abb2bf'}}>-&gt;</span> <span style={{color: '#61afef'}}>str</span><span style={{color: '#abb2bf'}}>:</span><br />
                {'    '}<span style={{color: '#98c379'}}>"""Calls an external weather API."""</span><br />
                {'    '}<span style={{color: '#61afef'}}>activity</span>.<span style={{color: '#e5c07b'}}>heartbeat</span>()  <span style={{color: '#5c6370'}}># Signals liveness</span><br />
                {'    '}<span style={{color: '#5c6370'}}>#... API call logic...</span><br />
                {'    '}<span style={{color: '#c678dd'}}>return</span> <span style={{color: '#98c379'}}>f"Sunny in </span><span style={{color: '#d19a66'}}>{'{'}city{'}'}</span><span style={{color: '#98c379'}}>."</span>
              </code>
            </pre>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <h3 className="font-semibold text-2xl md:text-3xl mb-4 text-blue-900">2. Define Agent Logic as a Workflow</h3>
            <p className="mb-4 text-lg md:text-xl text-blue-700">Orchestrate Activities. State is just a local variable.</p>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-base md:text-lg font-mono">
              <code>
                <span style={{color: '#5c6370'}}># workflows/agent_workflow.py</span><br />
                <span style={{color: '#c678dd'}}>from</span> <span style={{color: '#61afef'}}>temporalio</span> <span style={{color: '#c678dd'}}>import</span> <span style={{color: '#61afef'}}>workflow</span><br />
                <span style={{color: '#c678dd'}}>from</span> <span style={{color: '#61afef'}}>activities.tools</span> <span style={{color: '#c678dd'}}>import</span> <span style={{color: '#61afef'}}>get_weather</span><br />
                <br />
                <span style={{color: '#abb2bf'}}>@</span><span style={{color: '#61afef'}}>workflow</span>.<span style={{color: '#e5c07b'}}>define</span><br />
                <span style={{color: '#c678dd'}}>class</span> <span style={{color: '#e5c07b'}}>AgentWorkflow</span><span style={{color: '#abb2bf'}}>:</span><br />
                {'    '}<span style={{color: '#abb2bf'}}>@</span><span style={{color: '#61afef'}}>workflow</span>.<span style={{color: '#e5c07b'}}>run</span><br />
                {'    '}<span style={{color: '#c678dd'}}>async</span> <span style={{color: '#c678dd'}}>def</span> <span style={{color: '#e5c07b'}}>run</span>(<span style={{color: '#61afef'}}>self</span>, <span style={{color: '#61afef'}}>query</span><span style={{color: '#abb2bf'}}>:</span> <span style={{color: '#61afef'}}>str</span>) <span style={{color: '#abb2bf'}}>-&gt;</span> <span style={{color: '#61afef'}}>list</span>[<span style={{color: '#61afef'}}>str</span>]<span style={{color: '#abb2bf'}}>:</span><br />
                {'        '}<span style={{color: '#61afef'}}>results</span> <span style={{color: '#abb2bf'}}>=</span> []<br />
                {'        '}<span style={{color: '#5c6370'}}>#... agentic loop logic...</span><br />
                {'        '}<span style={{color: '#61afef'}}>summary</span> <span style={{color: '#abb2bf'}}>=</span> <span style={{color: '#c678dd'}}>await</span> <span style={{color: '#61afef'}}>workflow</span>.<span style={{color: '#e5c07b'}}>execute_activity</span>(<br />
                {'            '}<span style={{color: '#61afef'}}>get_weather</span>, <span style={{color: '#98c379'}}>"San Francisco"</span>,<br />
                {'            '}<span style={{color: '#61afef'}}>start_to_close_timeout</span><span style={{color: '#abb2bf'}}>=</span><span style={{color: '#e5c07b'}}>timedelta</span>(<span style={{color: '#61afef'}}>minutes</span><span style={{color: '#abb2bf'}}>=</span><span style={{color: '#d19a66'}}>1</span>)<br />
                {'        '})<br />
                {'        '}<span style={{color: '#61afef'}}>results</span>.<span style={{color: '#e5c07b'}}>append</span>(<span style={{color: '#61afef'}}>summary</span>)<br />
                {'        '}<span style={{color: '#c678dd'}}>return</span> <span style={{color: '#61afef'}}>results</span>
              </code>
            </pre>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 10,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">Implementation: Academic Research Agent</h2>
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-6 bg-white rounded-lg border-2 border-gray-300">
              <h3 className="text-2xl font-semibold mb-3 text-gray-800">Frontend</h3>
              <ul className="space-y-2 text-lg text-gray-700">
                <li>• Next.js chat interface</li>
                <li>• AI SDK for streaming</li>
                <li>• Real-time progress updates</li>
              </ul>
            </div>
            <div className="p-6 bg-gray-50 rounded-lg border-2 border-gray-300">
              <h3 className="text-2xl font-semibold mb-3 text-gray-800">Backend</h3>
              <ul className="space-y-2 text-lg text-gray-700">
                <li>• Python Temporal worker</li>
                <li>• arXiv MCP client</li>
                <li>• PDF processor</li>
                <li>• Citation analyzer</li>
              </ul>
            </div>
          </div>
          <div className="p-6 bg-green-50 rounded-lg border-l-4 border-green-600">
            <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-gray-800">Key Features</h3>
            <ul className="grid md:grid-cols-2 gap-4 text-xl md:text-2xl text-gray-700">
              <li>✓ Natural language queries</li>
              <li>✓ Parallel paper processing</li>
              <li>✓ Citation network visualization</li>
              <li>✓ Complete audit trail</li>
              <li>✓ Human-in-the-loop validation</li>
              <li>✓ Persistent chat history</li>
            </ul>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 11,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">Demo: Agent Comparison</h2>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div>
            <div className="mb-4 p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
              <h3 className="text-xl md:text-2xl font-bold text-red-900">GPT-5 Reasoning</h3>
              <p className="text-lg md:text-xl text-red-700 mt-2">OpenAI's latest reasoning model</p>
            </div>
            <img src="/presentation/gpt5-reasoning.jpeg" alt="GPT-5 Reasoning Agent" className="w-2/3 mx-auto rounded-lg shadow-lg border-2 border-gray-300" />
          </div>

          <div>
            <div className="mb-4 p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
              <h3 className="text-xl md:text-2xl font-bold text-green-900">Deep Research (arXiv powered)</h3>
              <p className="text-lg md:text-xl text-green-700 mt-2">GPT-4.1 mini + Temporal durability</p>
            </div>
            <img src="/presentation/myown-dr.jpeg" alt="Deep Research Agent with Temporal" className="w-2/3 mx-auto rounded-lg shadow-lg border-2 border-gray-300" />
          </div>
        </div>

        <div className="p-6 bg-amber-50 rounded-lg border-l-4 border-amber-500">
          <p className="text-xl md:text-2xl font-semibold text-center text-amber-900">
            <strong>Result:</strong> GPT-5 Reasoning is <span className="text-red-700">completely wrong</span> and <span className="text-red-700">more expensive</span>.
            Our durable agent with GPT-4.1 mini is <span className="text-green-700">correct</span> and <span className="text-green-700">cheaper</span>.
          </p>
        </div>
      </div>
    )
  },
  {
    id: 12,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">Demo: Temporal Web UI - Complete Observability</h2>
        <div className="space-y-6">
          <p className="text-xl md:text-2xl text-gray-700">Every step is recorded for academic integrity and reproducibility</p>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-6 bg-white rounded-lg border-2 border-gray-300">
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">Audit Trail Features</h3>
              <ul className="space-y-3 text-lg text-gray-700">
                <li className="flex items-start"><span className="mr-2 text-gray-500">•</span> Complete event history</li>
                <li className="flex items-start"><span className="mr-2 text-gray-500">•</span> Activity inputs/outputs</li>
                <li className="flex items-start"><span className="mr-2 text-gray-500">•</span> Retry attempts visible</li>
                <li className="flex items-start"><span className="mr-2 text-gray-500">•</span> Timeline visualization</li>
                <li className="flex items-start"><span className="mr-2 text-gray-500">•</span> Error stack traces</li>
              </ul>
            </div>
            <div className="p-6 bg-green-50 rounded-lg border-l-4 border-green-600">
              <h3 className="text-2xl font-semibold mb-4 text-gray-800">Benefits for Academia</h3>
              <ul className="space-y-3 text-lg text-gray-700">
                <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> Supervisor verification</li>
                <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> Reproducible results</li>
                <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> Debug failed searches</li>
                <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> Research ethics compliance</li>
                <li className="flex items-start"><span className="text-green-600 mr-2">✓</span> Citation validation</li>
              </ul>
            </div>
          </div>
          <div className="p-6 bg-gray-50 rounded-lg border-2 border-gray-300">
            <p className="text-xl text-center"><strong>Transparent vs. Black Box:</strong> Traditional agents provide no insight into their process</p>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 13,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">Evaluation: Real PhD Research Benchmark</h2>

        <div className="mb-6 p-6 bg-blue-50 rounded-lg border-l-4 border-blue-500">
          <p className="text-xl md:text-2xl font-semibold text-blue-900"><strong>Task:</strong> Search & summarize 100 papers for PhD thesis writing process</p>
          <p className="text-lg md:text-xl text-blue-700 mt-2">Same Tier-1 API account with rate limitations • <em className="text-sm">Lower is better ↓</em></p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-6">
          {/* Hallucination Rate */}
          <div>
            <h3 className="text-lg md:text-xl font-bold mb-3 text-gray-800">Hallucination Rate</h3>
            <div className="space-y-2">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm md:text-base font-semibold">GPT-5</span>
                  <span className="text-sm md:text-base font-bold text-red-600">24%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div className="bg-red-500 h-6 rounded-full" style={{width: '61.5%'}}></div>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm md:text-base font-semibold">Claude</span>
                  <span className="text-sm md:text-base font-bold text-red-600">39%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div className="bg-red-600 h-6 rounded-full" style={{width: '100%'}}></div>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm md:text-base font-semibold">Ours</span>
                  <span className="text-sm md:text-base font-bold text-green-600">5% ✓</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div className="bg-green-500 h-6 rounded-full" style={{width: '12.8%'}}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Failure Rate */}
          <div>
            <h3 className="text-lg md:text-xl font-bold mb-3 text-gray-800">Failure Rate</h3>
            <div className="space-y-2">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm md:text-base font-semibold">GPT-5</span>
                  <span className="text-sm md:text-base font-bold text-red-600">15%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div className="bg-red-500 h-6 rounded-full" style={{width: '75%'}}></div>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm md:text-base font-semibold">Claude</span>
                  <span className="text-sm md:text-base font-bold text-red-600">20%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div className="bg-red-600 h-6 rounded-full" style={{width: '100%'}}></div>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm md:text-base font-semibold">Ours</span>
                  <span className="text-sm md:text-base font-bold text-green-600">&lt;2% ✓</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div className="bg-green-500 h-6 rounded-full" style={{width: '10%'}}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Token Consumption */}
          <div>
            <h3 className="text-lg md:text-xl font-bold mb-3 text-gray-800">Token Cost</h3>
            <div className="space-y-2">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm md:text-base font-semibold">GPT-5</span>
                  <span className="text-sm md:text-base font-bold text-red-600">100%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div className="bg-red-500 h-6 rounded-full" style={{width: '100%'}}></div>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm md:text-base font-semibold">Claude</span>
                  <span className="text-sm md:text-base font-bold text-orange-600">70%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div className="bg-orange-500 h-6 rounded-full" style={{width: '70%'}}></div>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm md:text-base font-semibold">Ours</span>
                  <span className="text-sm md:text-base font-bold text-green-600">15% ✓</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6">
                  <div className="bg-green-500 h-6 rounded-full" style={{width: '15%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="p-6 bg-green-50 rounded-lg border-l-4 border-green-500">
            <h3 className="text-2xl md:text-3xl font-bold mb-3 text-green-900">Temporal + arXiv MCP</h3>
            <ul className="space-y-2 text-lg md:text-xl text-green-700">
              <li>✓ 85% cheaper than GPT-5 Reasoning</li>
              <li>✓ 5x more accurate (5% vs 24% hallucination)</li>
              <li>✓ 7.5x more reliable (&lt;2% vs 15% failure)</li>
              <li>✓ Durable execution prevents data loss</li>
            </ul>
          </div>
          <div className="p-6 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <h3 className="text-2xl md:text-3xl font-bold mb-3 text-blue-900">Key Insight</h3>
            <p className="text-lg md:text-xl text-blue-700"><strong>Architecture matters more than model size.</strong> A smaller model (GPT-4.1 mini) with proper infrastructure (Temporal + arXiv MCP) outperforms larger models significantly.</p>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 14,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">Key Takeaways & Impact</h2>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div className="p-6 bg-green-50 rounded-lg border-l-4 border-green-600">
            <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-green-900">Performance Results</h3>
            <ul className="space-y-3 text-lg md:text-xl text-green-800">
              <li><strong>5%</strong> hallucination vs 24-39% (GPT-5/Claude)</li>
              <li><strong>&lt;2%</strong> failure rate vs 15-20%</li>
              <li><strong>85%</strong> cost reduction vs GPT-5 Reasoning</li>
              <li><strong>10x faster</strong> than manual research</li>
              <li><strong>100 papers</strong> processed for PhD citations</li>
            </ul>
          </div>

          <div className="p-6 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-blue-900">Critical Insights</h3>
            <ul className="space-y-3 text-lg md:text-xl text-blue-800">
              <li>Event sourcing: <strong>~5% overhead → 100% reliability</strong></li>
              <li>Architecture matters <strong>more than model size</strong></li>
              <li>HITL checkpoints essential for academic integrity</li>
              <li>Deterministic workflows + non-deterministic activities</li>
            </ul>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div className="p-6 bg-purple-50 rounded-lg border-l-4 border-purple-600">
            <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-purple-900">Impact for PhD Students</h3>
            <ul className="space-y-3 text-lg md:text-xl text-purple-800">
              <li><strong>Trustworthy</strong> for thesis work</li>
              <li>Supervisor can <strong>audit</strong> complete process</li>
              <li><strong>Reproducible</strong> and verifiable reviews</li>
              <li>Academic <strong>integrity</strong> maintained</li>
            </ul>
          </div>

          <div className="p-6 bg-amber-50 rounded-lg border-l-4 border-amber-600">
            <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-amber-900">Limitations</h3>
            <ul className="space-y-3 text-lg md:text-xl text-amber-800">
              <li>Temporal infrastructure setup required</li>
              <li>1-2 day learning curve for workflow programming</li>
              <li>API costs scale with paper count (still cheaper than human)</li>
            </ul>
          </div>
        </div>

        <div className="p-6 bg-gray-100 rounded-lg border-l-4 border-gray-600">
          <h3 className="text-2xl md:text-3xl font-semibold mb-4 text-gray-800">Next Steps</h3>
          <ul className="space-y-3 text-lg md:text-xl text-gray-700">
            <li><strong>Try it:</strong> GitHub repo with Docker Compose setup</li>
            <li><strong>Extend it:</strong> Add more MCP servers (Wikipedia, PubMed, etc.)</li>
            <li><strong>Scale it:</strong> Multi-agent workflows for complex research</li>
          </ul>
        </div>
      </div>
    )
  },
  {
    id: 16,
    content: (
      <div className="slide-content">
        <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gray-800">References</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-2" style={{color: '#00549f'}}>AI Agents & Agentic Systems</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[1] Xi, Z., et al. (2024). "The Rise and Potential of LLM Based Agents." arXiv:2309.07864</li>
              <li>[2] Wang, L., et al. (2024). "A Survey on LLM based Autonomous Agents." arXiv:2308.11432</li>
              <li>[3] Yao, S., et al. (2023). "ReAct: Synergizing Reasoning and Acting." arXiv:2210.03629</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Distributed Systems & Fault Tolerance</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[18] Kleppmann, M. (2017). "Designing Data-Intensive Applications." O'Reilly</li>
              <li>[19] Temporal Technologies. (2023). "Durable Execution Whitepaper."</li>
              <li>[20] Dean, J., & Barroso, L. (2013). "Tail at Scale." Communications ACM, 56(2)</li>
              <li>[28] Fowler, M. (2005). "Event Sourcing Pattern." martinfowler.com</li>
              <li>[29] Richardson, C. (2018). "Microservices Patterns." Manning Publications</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>LLM Reliability & Hallucination</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[9] Zhang, Y., et al. (2023). "Siren's Song: Hallucination in LLMs." arXiv:2309.01219</li>
              <li>[10] Liu, J., et al. (2024). "AgentBench: Evaluating LLMs as Agents." arXiv:2308.03688</li>
              <li>[16] Ji, Z., et al. (2023). "Hallucination Survey." ACM Computing Surveys, 55(12)</li>
              <li>[22] Manakul, P., et al. (2023). "SelfCheckGPT." arXiv:2303.08896</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Tool Use & Integration</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[11] Schick, T., et al. (2024). "Toolformer." arXiv:2302.04761</li>
              <li>[12] Patil, S., et al. (2023). "Gorilla: LLM Connected with APIs." arXiv:2305.15334</li>
              <li>[23] Qin, Y., et al. (2023). "Tool Learning with LLMs." arXiv:2304.08354</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Multi-Agent Systems</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[31] Hong, S., et al. (2023). "MetaGPT: Multi-Agent Framework." arXiv:2308.00352</li>
              <li>[32] Qian, C., et al. (2023). "Communicative Agents." arXiv:2307.07924</li>
              <li>[33] Park, P., et al. (2023). "Multi-Agent Collaboration." arXiv:2310.08560</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Agent Frameworks & Orchestration</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[36] LangChain Team. (2024). "LangGraph Documentation." python.langchain.com</li>
              <li>[39] Chase, H. (2023). "Building Production-Ready LLM Apps." LangChain Blog</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Memory & Self-Improvement</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[40] Packer, C., et al. (2023). "MemGPT: Memory Management." arXiv:2310.08560</li>
              <li>[41] Shinn, N., et al. (2023). "Reflexion: Self-Reflection." arXiv:2303.11366</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2" style={{color: '#00549f'}}>Security & Safety</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[25] Greshake, K., et al. (2023). "Prompt Injection Attacks." arXiv:2302.12173</li>
              <li>[42] Solaiman, I., et al. (2023). "AI Governance Framework." arXiv:2306.10124</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Scientific Workflows & HITL</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[7] Goecks, J., et al. (2010). "Galaxy." Genome Biology, 11:R86</li>
              <li>[8] Wolstencroft, K., et al. (2013). "Taverna." Nucleic Acids Research, 41</li>
              <li>[44] Amershi, S., et al. (2014). "Power to the People." ACM TIIS, 4(2)</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Literature Review Methods</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[15] Webster, J., & Watson, R. (2002). "Analyzing the Past." MIS Quarterly, 26(2)</li>
              <li>[43] Okoli, C., & Schabram, K. (2010). "Systematic Literature Reviews." Sprouts, 10(26)</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Publication Growth & Trends</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[46] NeurIPS. (2024). "NeurIPS 2024 Statistics." Paper Copilot & Official Fact Sheet</li>
              <li>[47] Azad, A., & Banu, A. (2024). "Publication Trends in AI Conferences." arXiv:2412.07793</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Industry Trends & Agentic AI</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[48] Anthropic. (2024). "Introducing Computer Use." anthropic.com/news/3-5-models-and-computer-use</li>
              <li>[49] Deutsche Telekom. (2024). "Agentic AI: Partnership with n8n." telekom.com</li>
              <li>[50] TechCrunch. (2025). "Manus AI Gets Funding at $500M Valuation." techcrunch.com</li>
              <li>[51] Gartner. (2024). "AI Agent Market Predictions: 33% of Enterprise Software by 2028."</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>AI Agent Reliability Evidence</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[52] Carnegie Mellon University. (2024). "TheAgentCompany: AI Agents 91-98% Failure Rate"</li>
              <li>[53] Replit. (2024). "Production Database Deletion Incident." Fortune & The Register</li>
              <li>[54] Moffatt v. Air Canada. (2024). "AI Chatbot Hallucination Lawsuit." BCCRT 149</li>
              <li>[55] Gartner. (2025). "40% of Agentic AI Projects Will Be Canceled by 2027"</li>
            </ul>
            <h3 className="text-lg font-semibold mb-2 mt-3" style={{color: '#00549f'}}>Agent Architecture & MCP</h3>
            <ul className="space-y-1 text-sm leading-tight">
              <li>[56] Anthropic. (2024). "Model Context Protocol (MCP) Documentation." modelcontextprotocol.io</li>
              <li>[57] NeurIPS. (2024). "Reflective Multi-Agent Collaboration." Proceedings NeurIPS 2024</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }
];

export default function PresentationPage() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const totalSlides = slides.length;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        nextSlide();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevSlide();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [currentSlide]);

  const nextSlide = () => {
    if (currentSlide < totalSlides - 1) {
      setCurrentSlide(currentSlide + 1);
    }
  };

  const prevSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(currentSlide - 1);
    }
  };

  return (
    <div className="bg-gray-100 text-gray-800 antialiased">
      <div className="container mx-auto p-4 md:p-8">
        <div className="bg-gray-50 rounded-2xl shadow-2xl overflow-hidden min-h-[85vh] flex flex-col">
          
          {/* Slides Container */}
          <div className="flex-grow p-8 md:p-12 lg:p-16 relative">
            <div className="slide active">
              <div className="slide-content flex flex-col justify-center min-h-[80vh]">
                {slides[currentSlide].content}
              </div>
            </div>

            {/* RWTH Logo - Bottom Right */}
            <div className="absolute bottom-4 right-4 md:bottom-8 md:right-8">
              <img
                src="/presentation/rwth_i5_en_rgb.svg"
                alt="RWTH Aachen University"
                className="w-48 md:w-56 lg:w-64 opacity-90"
              />
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between p-4 bg-gray-50 border-t border-gray-200">
            <button
              onClick={prevSlide}
              disabled={currentSlide === 0}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 px-6 text-lg rounded-lg transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <div className="text-gray-600 font-medium text-lg md:text-xl">
              Slide {currentSlide + 1} / {totalSlides}
            </div>
            <button
              onClick={nextSlide}
              disabled={currentSlide === totalSlides - 1}
              className="text-white font-bold py-3 px-6 text-lg rounded-lg transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{backgroundColor: '#00549f'}}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#407fb7'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#00549f'}
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <style jsx global>{`
        body {
          font-family: 'Inter', sans-serif;
          background-color: #f0f2f5;
        }
        .slide {
          display: block;
          opacity: 1;
          transition: opacity 0.5s ease-in-out;
        }
        .slide-content {
          display: flex;
          flex-direction: column;
          justify-content: center;
          min-height: 80vh;
        }
        .code-snippet {
          background-color: #1e293b;
          color: #f8fafc;
          padding: 1rem;
          border-radius: 0.5rem;
          overflow-x: auto;
          font-family: monospace;
        }
        table {
          width: 100%;
          border-collapse: collapse;
        }
        th, td {
          border: 1px solid #d1d5db;
          padding: 0.75rem;
          text-align: left;
        }
        th {
          background-color: #f3f4f6;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
}